"""
MongoDB handler module for document metadata storage.
Manages CRUD operations for document metadata.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from config import Config


class MongoDBHandler:
    """Handles MongoDB operations for document metadata"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            db_name = Config.MONGODB_URI.split('/')[-1] or 'docuquery'
            self.db = self.client[db_name]
            self.collection = self.db['documents']
            
            # Create index on document_id for faster queries
            self.collection.create_index([('document_id', ASCENDING)], unique=True)
            
        except ConnectionFailure as e:
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")
    
    def insert_document(self, filename: str, chunk_count: int, file_path: str = None) -> str:
        """
        Insert document metadata into database
        
        Args:
            filename: Name of the uploaded file
            chunk_count: Number of chunks created from the document
            file_path: Optional path to the stored file
            
        Returns:
            Document ID
        """
        document_id = str(uuid.uuid4())
        
        document = {
            'document_id': document_id,
            'filename': filename,
            'chunk_count': chunk_count,
            'file_path': file_path,
            'upload_time': datetime.utcnow(),
            'status': 'processed'
        }
        
        try:
            self.collection.insert_one(document)
            return document_id
        except DuplicateKeyError:
            raise Exception(f"Document with ID {document_id} already exists")
        except Exception as e:
            raise Exception(f"Error inserting document: {str(e)}")
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """
        Retrieve document metadata by ID
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document metadata or None if not found
        """
        try:
            document = self.collection.find_one(
                {'document_id': document_id},
                {'_id': 0}  # Exclude MongoDB's internal ID
            )
            return document
        except Exception as e:
            raise Exception(f"Error retrieving document: {str(e)}")
    
    def get_all_documents(self) -> List[Dict]:
        """
        Retrieve all document metadata
        
        Returns:
            List of document metadata
        """
        try:
            documents = list(self.collection.find(
                {},
                {'_id': 0}  # Exclude MongoDB's internal ID
            ).sort('upload_time', -1))  # Sort by most recent first
            return documents
        except Exception as e:
            raise Exception(f"Error retrieving documents: {str(e)}")
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete document metadata from database
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            result = self.collection.delete_one({'document_id': document_id})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    def update_document_status(self, document_id: str, status: str) -> bool:
        """
        Update document processing status
        
        Args:
            document_id: ID of the document
            status: New status (e.g., 'processing', 'processed', 'failed')
            
        Returns:
            True if updated, False if not found
        """
        try:
            result = self.collection.update_one(
                {'document_id': document_id},
                {'$set': {'status': status, 'updated_time': datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error updating document status: {str(e)}")
    
    def get_document_count(self) -> int:
        """
        Get total number of documents
        
        Returns:
            Number of documents
        """
        try:
            return self.collection.count_documents({})
        except Exception as e:
            raise Exception(f"Error counting documents: {str(e)}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
