from src.embeddings import EmbeddingManager
from src.agent import ResearchAgent
import os
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key and verify it exists
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file!")
        return
        
    print("API Key loaded successfully!")
    
    # Test documents
    docs = [
        "RAG (Retrieval Augmented Generation) systems combine document retrieval with language models. They help provide more accurate and current information.",
        "NVIDIA's latest GPUs feature Tensor Cores specifically designed for AI workloads. These cores accelerate matrix multiplication operations.",
        "LangChain is a framework that helps developers build AI applications by providing tools for working with language models and creating agents.",
        "Agentic AI refers to AI systems that can autonomously plan and execute tasks. These systems often use tools and make decisions based on context."
    ]
    
    try:
        print("Creating embeddings...")
        embedding_manager = EmbeddingManager()
        embedding_manager.create_embeddings(docs)
        
        print("\nInitializing agent...")
        agent = ResearchAgent(api_key=api_key)
        
        questions = [
            "What is RAG and how does it work?",
            "How does LangChain help in building AI applications?"
        ]
        
        print("\nTesting agent responses...")
        for question in questions:
            print(f"\nQuestion: {question}")
            answer = agent.answer_question(question)
            print(f"Answer: {answer}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()