"""
Vector database interface for the AI Learning Path Generator.
Handles document storage, retrieval, and semantic search.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_core.documents import Document

from src.utils.config import VECTOR_DB_PATH, OPENAI_API_KEY

class DocumentStore:
    """
    Enhanced document retrieval using ChromaDB vector database.
    Supports semantic search, filtering, and relevance ranking.
    """
    def __init__(self, db_path: Optional[str] = None):
        print(f"--- DocumentStore.__init__ started (db_path: {db_path or VECTOR_DB_PATH}) ---")
        """
        Initialize the document store.
        
        Args:
            db_path: Optional path to the vector database
        """
        self.db_path = db_path or VECTOR_DB_PATH
        
        # Ensure the directory exists
        os.makedirs(self.db_path, exist_ok=True)
        print(f"--- DocumentStore.__init__: Ensured directory exists: {self.db_path} ---")
        
        print("--- DocumentStore.__init__: Initializing chromadb.PersistentClient ---")
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        print("--- DocumentStore.__init__: chromadb.PersistentClient initialized ---")
        
        # Set up OpenAI embedding function
        print(f"--- DocumentStore.__init__: Initializing OpenAIEmbeddings with model: text-embedding-ada-002 ---")
        print(f"--- DocumentStore.__init__: Initializing OpenAIEmbeddingFunction (model: text-embedding-ada-002, API key starts with: {str(OPENAI_API_KEY)[:15]}...) ---")
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-ada-002"
        )
        print("--- DocumentStore.__init__: OpenAIEmbeddingFunction initialized ---")
        
        # Create or get the collections
        print("--- DocumentStore.__init__: Getting/creating 'learning_resources' collection ---")
        self.resources_collection = self.client.get_or_create_collection(
            name="learning_resources",
            embedding_function=self.embedding_function,
            metadata={"description": "Educational resources and materials"}
        )
        print("--- DocumentStore.__init__: 'learning_resources' collection obtained ---")
        
        print("--- DocumentStore.__init__: Getting/creating 'learning_paths' collection ---")
        self.paths_collection = self.client.get_or_create_collection(
            name="learning_paths",
            embedding_function=self.embedding_function,
            metadata={"description": "Generated learning paths"}
        )
        print("--- DocumentStore.__init__: 'learning_paths' collection obtained ---")
        print("--- DocumentStore.__init__ finished ---")
    
    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        collection_name: str = "learning_resources",
        document_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the vector database.
        
        Args:
            content: Document content
            metadata: Document metadata
            collection_name: Name of the collection to add to
            document_id: Optional ID for the document
            
        Returns:
            ID of the added document
        """
        # Generate a document ID if not provided
        doc_id = document_id or f"doc_{len(content) % 10000}_{hash(content) % 1000000}"
        
        # Get the appropriate collection
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        
        # Add the document
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def add_documents(
        self, 
        documents: List[Document],
        collection_name: str = "learning_resources"
    ) -> List[str]:
        """
        Add multiple documents to the vector database.
        
        Args:
            documents: List of Document objects
            collection_name: Name of the collection to add to
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        # Get the appropriate collection
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        
        # Prepare document data
        contents = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"doc_{i}_{hash(doc.page_content) % 1000000}" for i, doc in enumerate(documents)]
        
        # Add documents in batches (ChromaDB has limits)
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_end = min(i + batch_size, len(documents))
            collection.add(
                documents=contents[i:batch_end],
                metadatas=metadatas[i:batch_end],
                ids=ids[i:batch_end]
            )
        
        return ids
    
    def search_documents(
        self,
        query: str,
        collection_name: str = "learning_resources",
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Document]:
        """
        Search for documents using semantic similarity.
        
        Args:
            query: Search query
            collection_name: Collection to search in
            filters: Optional metadata filters
            top_k: Number of results to return
            
        Returns:
            List of relevant Document objects
        """
        # Get the collection
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except Exception:
            # Collection doesn't exist
            return []
        
        # Prepare filter if provided
        where = {}
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    # For list values, we need to use the $in operator
                    where[key] = {"$in": value}
                else:
                    where[key] = value
        
        # Execute the search
        try:
            result = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where if where else None
            )
        except Exception:
            # Search failed
            return []
        
        # Convert results to Document objects
        documents = []
        if result and result.get("documents"):
            for i, content in enumerate(result["documents"][0]):
                metadata = result["metadatas"][0][i] if result.get("metadatas") and result["metadatas"][0] else {}
                distance = result["distances"][0][i] if result.get("distances") and result["distances"][0] else 1.0
                
                # Add relevance score to metadata
                metadata["relevance_score"] = 1.0 - (distance / 2.0)  # Convert distance to relevance (0-1)
                
                documents.append(Document(
                    page_content=content,
                    metadata=metadata
                ))
        
        return documents
    
    def hybrid_search(
        self,
        query: str,
        collection_name: str = "learning_resources",
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Document]:
        """
        Perform hybrid search combining semantic and keyword matching.
        
        Args:
            query: Search query
            collection_name: Collection to search in
            filters: Optional metadata filters
            top_k: Number of results to return
            
        Returns:
            List of relevant Document objects
        """
        # First, get semantic search results
        semantic_results = self.search_documents(
            query=query,
            collection_name=collection_name,
            filters=filters,
            top_k=top_k * 2  # Get more results for reranking
        )
        
        # Prepare keyword results for simple matching
        keyword_docs = []
        try:
            # Get all documents matching the filters
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            
            # Prepare filter for keyword search
            where = {}
            if filters:
                where.update(filters)
            
            # Get documents matching the filter
            result = collection.get(where=where if where else None)
            
            if result and result.get("documents"):
                # Simple keyword matching
                query_terms = set(query.lower().split())
                
                for i, content in enumerate(result["documents"]):
                    # Count matching terms in content
                    content_lower = content.lower()
                    match_count = sum(1 for term in query_terms if term in content_lower)
                    
                    if match_count > 0:
                        metadata = result["metadatas"][i] if result.get("metadatas") else {}
                        # Score based on ratio of matching terms
                        metadata["relevance_score"] = match_count / len(query_terms)
                        
                        keyword_docs.append(Document(
                            page_content=content,
                            metadata=metadata
                        ))
        except Exception:
            # Keyword search failed, continue with semantic results only
            pass
        
        # Combine results, removing duplicates
        all_docs = {}
        
        # Add semantic results
        for doc in semantic_results:
            doc_key = hash(doc.page_content)
            all_docs[doc_key] = doc
        
        # Add keyword results that don't duplicate semantic results
        for doc in keyword_docs:
            doc_key = hash(doc.page_content)
            if doc_key not in all_docs:
                all_docs[doc_key] = doc
        
        # Sort by relevance score and return top_k
        sorted_docs = sorted(
            all_docs.values(),
            key=lambda x: x.metadata.get("relevance_score", 0),
            reverse=True
        )
        
        return sorted_docs[:top_k]
    
    def delete_document(
        self,
        document_id: str,
        collection_name: str = "learning_resources"
    ) -> bool:
        """
        Delete a document from the vector database.
        
        Args:
            document_id: ID of the document to delete
            collection_name: Collection to delete from
            
        Returns:
            Success status
        """
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            
            collection.delete(ids=[document_id])
            return True
        except Exception:
            return False
    
    def clear_collection(self, collection_name: str) -> bool:
        """
        Clear all documents from a collection.
        
        Args:
            collection_name: Collection to clear
            
        Returns:
            Success status
        """
        try:
            self.client.delete_collection(collection_name)
            self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            return True
        except Exception:
            return False
