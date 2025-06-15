"""
Vector store implementation for RAG capabilities.
"""
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.directory import DirectoryLoader

class VectorStore:
    """
    Manages vector storage for RAG capabilities.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            api_key: Optional OpenAI API key
        """
        self.api_key = api_key
        
        # Use the latest LangChain OpenAI embeddings
        # This works with openai v1.0.0+ as LangChain handles the API compatibility
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
            
        self.vector_store_path = Path("vector_db")
        self.vector_store_path.mkdir(exist_ok=True)
        self.vector_store = None

    def load_documents(self, directory: str = None) -> None:
        """
        Load documents from a directory and create embeddings.
        If no directory is provided, creates a minimal default vector store.
        
        Args:
            directory: Optional path to directory containing documents
        """
        try:
            # If no directory provided, create a minimal vector store
            if directory is None:
                self._create_minimal_vector_store()
                return
                
            # Check if directory exists
            if not os.path.exists(directory):
                print(f"Warning: Document directory {directory} not found. Creating minimal vector store.")
                self._create_minimal_vector_store()
                return
                
            # Try to load documents
            loader = DirectoryLoader(directory)
            documents = loader.load()
            
            if not documents:
                print("Warning: No documents found in directory. Creating minimal vector store.")
                self._create_minimal_vector_store()
                return
            
            # Process documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
            
            texts = text_splitter.split_documents(documents)
            
            # Create or update vector store
            if os.path.exists(self.vector_store_path / "index.faiss"):
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path),
                    self.embeddings
                )
                self.vector_store.add_documents(texts)
            else:
                self.vector_store = FAISS.from_documents(
                    texts,
                    self.embeddings
                )
                self.vector_store.save_local(str(self.vector_store_path))
                
        except Exception as e:
            print(f"Error loading documents: {str(e)}")
            self._create_minimal_vector_store()
    
    def _create_minimal_vector_store(self) -> None:
        """Create a minimal vector store with default content."""
        try:
            default_texts = [
                "This is a default document. The vector store was initialized with minimal content.",
                "You can add your own documents to the vector store by placing them in the vector_db/documents directory.",
                "The application will automatically load and index any text files found in that directory."
            ]
            
            if os.path.exists(self.vector_store_path / "index.faiss"):
                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path),
                    self.embeddings
                )
            else:
                self.vector_store = FAISS.from_texts(
                    default_texts,
                    self.embeddings
                )
                self.vector_store.save_local(str(self.vector_store_path))
                
        except Exception as e:
            print(f"Error creating minimal vector store: {str(e)}")
            # Create an empty FAISS index as a last resort
            self.vector_store = FAISS.from_texts(
                ["Default document"],
                self.embeddings
            )

    def search(self, query: str, k: int = 4, documents: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on query.
        
        Args:
            query: Search query
            k: Number of results to return
            documents: Optional list of documents to search through (fallback)
            
        Returns:
            List of relevant documents with scores
        """
        # If vector store is not available, fall back to simple text search
        if not self.vector_store:
            if not documents:
                return []
                
            # Simple text-based search as fallback
            query = query.lower()
            return [
                {"content": doc, "score": 1.0, "metadata": {}}
                for doc in documents
                if query in doc.lower()
            ][:k]
            
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": getattr(doc, 'metadata', {}),
                    "score": float(score) if hasattr(score, '__float__') else 0.0
                })
            return formatted_results
            
        except Exception as e:
            print(f"Error in vector store search: {str(e)}")
            # Fall back to simple text search if available
            if documents:
                query = query.lower()
                return [
                    {"content": doc, "score": 1.0, "metadata": {}}
                    for doc in documents
                    if query in doc.lower()
                ][:k]
            return []
