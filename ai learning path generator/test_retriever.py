from src.embeddings import EmbeddingManager
from src.retriever import DocumentRetriever

def main():
    # First, let's add some test documents
    docs = [
        "RAG systems help AI models access current information",
        "Neural networks learn patterns from training data",
        "LangChain is a framework for developing AI applications",
        "NVIDIA GPUs accelerate machine learning training"
    ]
    
    # Create embeddings for our docs
    print("Creating embeddings...")
    embedding_manager = EmbeddingManager()
    embedding_manager.create_embeddings(docs)
    
    # Test retrieval
    print("\nTesting retrieval...")
    retriever = DocumentRetriever()
    query = "How do RAG systems work?"
    results = retriever.retrieve_relevant_docs(query)
    
    print(f"\nQuery: {query}")
    print("Retrieved documents:")
    for doc in results['documents'][0]:
        print(f"- {doc}")

if __name__ == "__main__":
    main()