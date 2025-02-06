from src.embeddings import EmbeddingManager

# Test data
test_texts = [
    "Machine learning is a subset of artificial intelligence.",
    "RAG systems combine retrieval with generation.",
    "Neural networks are inspired by biological neurons.",
    "LangChain provides tools for building AI applications."
]

def main():
    embedding_manager = EmbeddingManager()
    embedding_manager.create_embeddings(test_texts)
    print("Embeddings created successfully!")

if __name__ == "__main__":
    main()