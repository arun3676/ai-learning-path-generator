# src/retriever.py

from chromadb.config import Settings
import chromadb
from typing import List, Dict

class DocumentRetriever:
    def __init__(self):
        # Initialize ChromaDB client - this is our vector database
        # Vector database stores document embeddings for efficient similarity search
        self.chroma_client = chromadb.Client(Settings(
            persist_directory='./data/chroma_db'
        ))
        
    def retrieve_relevant_docs(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Find documents relevant to a query using semantic search
        Parameters:
            query: The user's question
            n_results: How many similar documents to retrieve
        """
        # Get our collection of embedded documents
        collection = self.chroma_client.get_collection("research_docs")
        
        # Query the collection - this finds similar documents based on meaning
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return results