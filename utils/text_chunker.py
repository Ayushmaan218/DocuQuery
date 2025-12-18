"""
Text chunking module for splitting documents into manageable chunks.
Uses LangChain's RecursiveCharacterTextSplitter for semantic chunking.
"""

from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config


class TextChunker:
    """Handles intelligent text chunking with overlap"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize text chunker
        
        Args:
            chunk_size: Size of each chunk (default from config)
            chunk_overlap: Overlap between chunks (default from config)
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Prepare metadata
        base_metadata = metadata or {}
        
        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **base_metadata,
                'chunk_index': i,
                'chunk_total': len(chunks)
            }
            chunk_objects.append({
                'text': chunk,
                'metadata': chunk_metadata
            })
        
        return chunk_objects
    
    def get_chunk_count(self, text: str) -> int:
        """
        Get the number of chunks that will be created
        
        Args:
            text: Text to analyze
            
        Returns:
            Number of chunks
        """
        if not text or not text.strip():
            return 0
        return len(self.text_splitter.split_text(text))
