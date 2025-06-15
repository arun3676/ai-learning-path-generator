"""
Vector embedding utilities for the AI Learning Path Generator.
Handles text vectorization for semantic search.
"""
from typing import List, Dict, Any, Optional, Union
import numpy as np

# Import directly from langchain-openai instead of openai
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document

from src.utils.config import OPENAI_API_KEY, EMBEDDING_MODEL

class EmbeddingService:
    """
    Service for generating and managing text embeddings.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the embedding service.
        
        Args:
            api_key: Optional OpenAI API key
        """
        self.api_key = api_key or OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please provide it or set the OPENAI_API_KEY environment variable.")
        
        # Initialize the embedding model - langchain_openai handles the new API format internally
        self.embeddings = OpenAIEmbeddings(
            api_key=self.api_key,
            model=EMBEDDING_MODEL
        )
        
        # Initialize text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for a text string.
        
        Args:
            text: The text to embed
            
        Returns:
            Embedding vector as a list of floats
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            raise ValueError(f"Failed to generate document embeddings: {str(e)}")
    
    def chunk_text(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: The text to split
            metadata: Optional metadata to add to each chunk
            
        Returns:
            List of Document objects with text chunks
        """
        # Create a document with metadata
        doc = Document(page_content=text, metadata=metadata or {})
        
        # Split into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        return chunks
    
    def calculate_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1)
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0  # Handle zero vectors
        
        return dot_product / (norm1 * norm2)
