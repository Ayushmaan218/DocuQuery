"""
DocuQuery - RAG System Flask Application
Main Flask application with REST API endpoints for document upload and querying.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from config import Config
from utils.document_processor import DocumentProcessor
from utils.text_chunker import TextChunker
from utils.vector_store import VectorStoreManager
from utils.llm_handler import LLMHandler
from database.mongodb_handler import MongoDBHandler

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Validate configuration
Config.validate()

# Initialize components
vector_store_manager = VectorStoreManager()
llm_handler = LLMHandler()
db_handler = MongoDBHandler()
text_chunker = TextChunker()

# Load existing vector store if available
vector_store_manager.load_vector_store()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'vector_store_size': vector_store_manager.get_store_size(),
        'document_count': db_handler.get_document_count()
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a document
    
    Expected: multipart/form-data with 'file' field
    Returns: document_id, filename, chunk_count, status
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not DocumentProcessor.validate_file_extension(file.filename, Config.ALLOWED_EXTENSIONS):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Get user_id from form data (optional, for user-based filtering)
        user_id = request.form.get('user_id', 'anonymous')
        
        # Save file
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Process document
        try:
            # Extract text
            text = DocumentProcessor.process_document(file_path)
            
            if not text or not text.strip():
                return jsonify({'error': 'No text could be extracted from the document'}), 400
            
            # Chunk text
            chunks = text_chunker.chunk_text(text, metadata={'filename': filename})
            
            if not chunks:
                return jsonify({'error': 'Failed to create chunks from document'}), 400
            
            # Add to vector store
            chunk_count = vector_store_manager.add_documents_to_store(chunks)
            
            # Save vector store
            vector_store_manager.save_vector_store()
            
            # Store metadata in MongoDB
            document_id = db_handler.insert_document(
                filename=filename,
                chunk_count=chunk_count,
                file_path=file_path,
                user_id=user_id
            )
            
            return jsonify({
                'document_id': document_id,
                'filename': filename,
                'chunk_count': chunk_count,
                'status': 'processed',
                'message': 'Document uploaded and processed successfully'
            }), 201
        
        except Exception as e:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
    
    except Exception as e:
        return jsonify({'error': f'Error processing document: {str(e)}'}), 500


@app.route('/api/query', methods=['POST'])
def query_documents():
    """
    Query documents using natural language
    
    Expected JSON: {"query": "question", "top_k": 3}
    Returns: answer, sources, confidence
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        top_k = data.get('top_k', Config.TOP_K_RESULTS)
        
        # Search for relevant documents
        relevant_chunks = vector_store_manager.search_similar_documents(query, top_k=top_k)
        
        # Generate answer using LLM
        result = llm_handler.generate_answer(query, relevant_chunks)
        
        return jsonify({
            'query': query,
            'answer': result['answer'],
            'sources': result['sources'],
            'confidence': result['confidence'],
            'chunks_retrieved': len(relevant_chunks)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """
    Get list of all uploaded documents
    
    Returns: List of document metadata
    """
    try:
        documents = db_handler.get_all_documents()
        return jsonify({
            'documents': documents,
            'count': len(documents)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error retrieving documents: {str(e)}'}), 500


@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    Get specific document metadata
    
    Returns: Document metadata
    """
    try:
        document = db_handler.get_document(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify(document), 200
    
    except Exception as e:
        return jsonify({'error': f'Error retrieving document: {str(e)}'}), 500


@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Delete document metadata
    Note: Vector store vectors persist (requires rebuild for full deletion)
    
    Returns: Success message
    """
    try:
        # Get document info
        document = db_handler.get_document(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete from database
        deleted = db_handler.delete_document(document_id)
        
        if not deleted:
            return jsonify({'error': 'Failed to delete document'}), 500
        
        # Delete file if it exists
        if document.get('file_path') and os.path.exists(document['file_path']):
            os.remove(document['file_path'])
        
        return jsonify({
            'message': 'Document deleted successfully',
            'document_id': document_id,
            'note': 'Vector embeddings persist in FAISS index'
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("DocuQuery RAG System Starting...")
    print("=" * 50)
    print(f"Vector Store Size: {vector_store_manager.get_store_size()} documents")
    print(f"MongoDB Documents: {db_handler.get_document_count()}")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
