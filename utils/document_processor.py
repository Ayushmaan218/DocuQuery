"""
Document processor module for extracting text from various file formats.
Supports PDF, DOCX, and TXT files.
"""

import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document


class DocumentProcessor:
    """Handles document processing and text extraction"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text content
        """
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Extracted text content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    @staticmethod
    def process_document(file_path: str) -> str:
        """
        Process document and extract text based on file extension
        
        Args:
            file_path: Path to document file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Process based on file type
        if ext == '.pdf':
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return DocumentProcessor.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return DocumentProcessor.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
        """
        Validate if file extension is allowed
        
        Args:
            filename: Name of the file
            allowed_extensions: Set of allowed extensions
            
        Returns:
            True if extension is allowed, False otherwise
        """
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in allowed_extensions
