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
            self.users_collection = self.db['users']
            
            # Create index on document_id for faster queries
            self.collection.create_index([('document_id', ASCENDING)], unique=True)
            
            # Create index on username for faster user queries
            self.users_collection.create_index([('username', ASCENDING)], unique=True)
            
        except ConnectionFailure as e:
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")
    
    def insert_document(self, filename: str, chunk_count: int, file_path: str = None, user_id: str = 'anonymous') -> str:
        """
        Insert document metadata into database
        
        Args:
            filename: Name of the uploaded file
            chunk_count: Number of chunks created from the document
            file_path: Optional path to the stored file
            user_id: ID of the user who uploaded the document
            
        Returns:
            Document ID
        """
        document_id = str(uuid.uuid4())
        
        document = {
            'document_id': document_id,
            'filename': filename,
            'chunk_count': chunk_count,
            'file_path': file_path,
            'user_id': user_id,
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
    
    # User Authentication Methods
    
    def create_user(self, username: str, password_hash: str) -> Dict:
        """
        Create a new user account
        
        Args:
            username: Username
            password_hash: Hashed password
            
        Returns:
            User document with user_id
        """
        import hashlib
        user_id = hashlib.md5(username.encode()).hexdigest()
        
        user = {
            'username': username,
            'password_hash': password_hash,
            'user_id': user_id,
            'created_at': datetime.utcnow()
        }
        
        try:
            self.users_collection.insert_one(user)
            return {'user_id': user_id, 'username': username}
        except DuplicateKeyError:
            raise Exception("Username already exists")
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    def authenticate_user(self, username: str, password_hash: str) -> Optional[Dict]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password_hash: Hashed password
            
        Returns:
            User document if authenticated, None otherwise
        """
        try:
            user = self.users_collection.find_one(
                {'username': username, 'password_hash': password_hash},
                {'_id': 0, 'password_hash': 0}  # Exclude sensitive data
            )
            return user
        except Exception as e:
            raise Exception(f"Error authenticating user: {str(e)}")
    
    def get_user(self, username: str) -> Optional[Dict]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User document or None if not found
        """
        try:
            user = self.users_collection.find_one(
                {'username': username},
                {'_id': 0}
            )
            return user
        except Exception as e:
            raise Exception(f"Error retrieving user: {str(e)}")

