from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os
import textwrap

class EmbeddingManager:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Using a lightweight model that works well on your i5
        self.model = SentenceTransformer(model_name)
        self.chroma_client = chromadb.Client(Settings(
            persist_directory='./data/chroma_db'
        ))
        
    def create_embeddings(self, texts, collection_name='research_docs'):
        """Create embeddings for a list of texts"""
        # Get or create collection
        collection = self.chroma_client.get_or_create_collection(collection_name)
        
        # Generate embeddings in batches to manage memory
        batch_size = 32  # Adjusted for 8GB RAM
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            # Generate IDs for each document
            ids = [f"doc_{j}" for j in range(i, i + len(batch))]
            # Generate embeddings
            embeddings = self.model.encode(batch)
            # Add to collection
            collection.add(
                documents=batch,
                ids=ids
            )
            print(f"Processed batch {i//batch_size + 1}")