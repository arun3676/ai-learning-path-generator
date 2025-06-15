from src.learning_path import LearningPathGenerator
from src.embeddings import EmbeddingManager
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env file!")
        return
    
    # Initialize embedding manager and create some sample documents
    print("Initializing document database...")
    embedding_manager = EmbeddingManager()
    
    # Sample documents about various topics
    docs = [
        "Python is a high-level programming language known for its simplicity and readability. It's great for beginners.",
        "Python basics include variables, data types, loops, and functions. These are fundamental concepts for any programmer.",
        "Machine Learning is a subset of AI that focuses on creating systems that can learn from data.",
        "Key ML concepts include supervised learning, unsupervised learning, and reinforcement learning.",
        "Data Structures are ways of organizing and storing data. Common examples include arrays, linked lists, and trees.",
        "Basic data structures include lists, dictionaries, and sets in Python. These are essential for efficient programming.",
    ]
    
    # Create embeddings for our documents
    print("Creating document embeddings...")
    embedding_manager.create_embeddings(docs)
    
    # Initialize learning path generator
    print("\nInitializing learning path generator...")
    path_generator = LearningPathGenerator(api_key)
    
    # Test topics
    test_topics = [
        ("Python programming", "beginner"),
        ("Machine Learning", "intermediate"),
        ("Data Structures", "beginner")
    ]
    
    # Generate and test learning paths
    for topic, level in test_topics:
        print(f"\nGenerating learning path for {topic} ({level} level)...")
        try:
            learning_path = path_generator.generate_learning_path(topic, level)
            print("\nLearning Path:")
            print(learning_path)
            
            # Get estimated completion time
            time = path_generator.estimate_completion_time(learning_path)
            print(f"\nEstimated completion time: {time} hours")
            
            # Get prerequisites
            prereqs = path_generator.get_prerequisites(learning_path)
            print("\nPrerequisites:", prereqs)
            
        except Exception as e:
            print(f"Error generating learning path: {str(e)}")

if __name__ == "__main__":
    main()