# test_formatted_path.py
from src.core.learning_path import LearningPathGenerator
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: No API key found in .env file")
        return
    
    # Initialize generator
    generator = LearningPathGenerator(api_key)
    
    # Test topic
    topic = "Machine Learning with Python"
    level = "intermediate"
    
    print(f"Generating learning path for {topic}...")
    
    # Generate path
    path_data = generator.generate_structured_path(topic, level)
    
    # Print the raw data for debugging
    print("\nGenerated path data:")
    print(path_data)
    
    # Convert to markdown
    markdown_path = generator.format_as_markdown(path_data)
    
    # Save to file
    filename = f"{topic.lower().replace(' ', '_')}_path.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(markdown_path)
    
    print(f"\nLearning path has been saved to {filename}")

if __name__ == "__main__":
    main()