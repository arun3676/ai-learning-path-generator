"""
Initialize the vector database with sample educational resources.
This provides some starter content for the Learning Path Generator.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure OPENAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not set in environment variables")
    print("Please update your .env file with your API key")
    exit(1)

# Import after checking API key
from src.data.document_store import DocumentStore
from src.data.resources import ResourceManager
from langchain.schema.document import Document

def load_sample_resources():
    """Load sample resources from JSON file"""
    resources_path = Path("samples/sample_resources.json")
    
    if not resources_path.exists():
        # Create directory if it doesn't exist
        resources_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Create sample resources file with basic content
        sample_resources = [
            {
                "title": "Introduction to Machine Learning",
                "type": "course",
                "description": "A comprehensive beginner's course covering ML fundamentals",
                "difficulty": "beginner",
                "time_estimate": "10 hours",
                "url": "https://example.com/intro-ml",
                "topic": "machine learning",
                "learning_styles": ["visual", "reading"]
            },
            {
                "title": "Python for Data Science Handbook",
                "type": "book",
                "description": "Essential guide to using Python for data analysis and ML",
                "difficulty": "intermediate",
                "time_estimate": "20 hours",
                "url": "https://jakevdp.github.io/PythonDataScienceHandbook/",
                "topic": "python,data science",
                "learning_styles": ["reading"]
            },
            {
                "title": "Web Development Bootcamp",
                "type": "course",
                "description": "Full stack web development from scratch",
                "difficulty": "beginner",
                "time_estimate": "40 hours",
                "url": "https://example.com/web-dev-bootcamp",
                "topic": "web development",
                "learning_styles": ["visual", "kinesthetic"]
            },
            {
                "title": "Advanced JavaScript Patterns",
                "type": "video",
                "description": "Deep dive into advanced JS design patterns",
                "difficulty": "advanced",
                "time_estimate": "3 hours",
                "url": "https://example.com/js-patterns",
                "topic": "javascript",
                "learning_styles": ["visual", "auditory"]
            },
            {
                "title": "Spanish Learning Podcast",
                "type": "podcast",
                "description": "Learn Spanish through immersive audio lessons",
                "difficulty": "beginner",
                "time_estimate": "10 hours",
                "url": "https://example.com/spanish-podcast",
                "topic": "spanish,language learning",
                "learning_styles": ["auditory"]
            }
        ]
        
        with open(resources_path, "w") as f:
            json.dump(sample_resources, f, indent=2)
            
        print(f"Created sample resources file at {resources_path}")
        return sample_resources
    else:
        # Load existing resources
        with open(resources_path, "r") as f:
            return json.load(f)

def initialize_database():
    """Initialize the vector database with sample resources"""
    print("Initializing vector database...")
    
    # Create document store
    document_store = DocumentStore()
    
    # Load sample resources
    resources = load_sample_resources()
    
    # Convert to Document objects
    documents = []
    for resource in resources:
        # Create content from resource information
        content = f"""
        Title: {resource['title']}
        Description: {resource['description']}
        Type: {resource['type']}
        Difficulty: {resource['difficulty']}
        Topics: {resource.get('topic', '')}
        """
        
        # Create metadata
        metadata = {
            "title": resource["title"],
            "type": resource["type"],
            "difficulty": resource["difficulty"],
            "url": resource["url"],
            "topic": resource.get("topic", "").split(",")
        }
        
        # Add learning styles if available
        if "learning_styles" in resource:
            metadata["learning_styles"] = resource["learning_styles"]
        
        # Create document
        doc = Document(page_content=content, metadata=metadata)
        documents.append(doc)
    
    # Add documents to vector store
    document_store.add_documents(documents)
    print(f"Added {len(documents)} sample resources to vector database")
    
    # Test search functionality
    print("\nTesting search functionality...")
    results = document_store.search_documents("machine learning beginner", top_k=2)
    print(f"Found {len(results)} results for 'machine learning beginner'")
    for result in results:
        print(f"- {result.metadata.get('title')} (Relevance: {result.metadata.get('relevance_score', 0):.2f})")
    
    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    initialize_database()
