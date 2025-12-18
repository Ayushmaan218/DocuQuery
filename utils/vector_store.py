"""
Vector store module for managing FAISS index and embeddings.
Handles document embedding, storage, and similarity search.
"""

import os
import pickle
from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import Config


class VectorStoreManager:
    """Manages FAISS vector store operations"""
    
    def __init__(self):
        """Initialize vector store manager with OpenAI embeddings"""
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_key=Config.OPENAI_API_KEY
        )
        self.vector_store = None
        self.store_path = Config.VECTOR_STORE_PATH
    
    def create_vector_store(self, chunks: List[Dict]) -> int:
        """
        Create a new FAISS vector store from document chunks
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            raise ValueError("No chunks provided to create vector store")
        
        # Convert chunks to LangChain Document objects
        documents = [
            Document(page_content=chunk['text'], metadata=chunk['metadata'])
            for chunk in chunks
        ]
        
        # Create FAISS vector store
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        
        return len(documents)
    
    def add_documents_to_store(self, chunks: List[Dict]) -> int:
        """
        Add new documents to existing vector store
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            
        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0
        
        # Convert chunks to LangChain Document objects
        documents = [
            Document(page_content=chunk['text'], metadata=chunk['metadata'])
            for chunk in chunks
        ]
        
        if self.vector_store is None:
            # Create new store if none exists
            return self.create_vector_store(chunks)
        else:
            # Add to existing store
            self.vector_store.add_documents(documents)
            return len(documents)
    
    def search_similar_documents(self, query: str, top_k: int = None) -> List[Dict]:
        """
        Search for similar documents using semantic similarity
        
        Args:
            query: Search query
            top_k: Number of results to return (default from config)
            
        Returns:
            List of relevant chunks with metadata and similarity scores
        """
        if self.vector_store is None:
            return []
        
        k = top_k or Config.TOP_K_RESULTS
        
        # Perform similarity search with scores
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'text': doc.page_content,
                'metadata': doc.metadata,
                'similarity_score': float(score)
            })
        
        return formatted_results
    
    def save_vector_store(self, filename: str = "faiss_index") -> str:
        """
        Save FAISS vector store to disk
        
        Args:
            filename: Name of the file to save (without extension)
            
        Returns:
            Path to saved file
        """
        if self.vector_store is None:
            raise ValueError("No vector store to save")
        
        # Create directory if it doesn't exist
        os.makedirs(self.store_path, exist_ok=True)
        
        # Save FAISS index
        save_path = os.path.join(self.store_path, filename)
        self.vector_store.save_local(save_path)
        
        return save_path
    
    def load_vector_store(self, filename: str = "faiss_index") -> bool:
        """
        Load FAISS vector store from disk
        
        Args:
            filename: Name of the file to load (without extension)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        load_path = os.path.join(self.store_path, filename)
        
        if not os.path.exists(load_path):
            return False
        
        try:
            self.vector_store = FAISS.load_local(
                load_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return True
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def get_store_size(self) -> int:
        """
        Get the number of documents in the vector store
        
        Returns:
            Number of documents
        """
        if self.vector_store is None:
            return 0
        return self.vector_store.index.ntotal
