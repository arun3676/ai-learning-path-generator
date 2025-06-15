"""
Test script for direct OpenAI API implementation.
"""
import os
import sys
from dotenv import load_dotenv
from src.direct_openai import generate_completion

def test_direct_openai():
    # Load environment variables
    load_dotenv()
    
    # Test with a simple prompt
    test_prompt = "Hello, who won the world series in 2020?"
    
    print("Testing direct OpenAI API...")
    print(f"Using model: gpt-3.5-turbo")
    print(f"Prompt: {test_prompt}")
    
    try:
        response = generate_completion(
            prompt=test_prompt,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100,
            timeout=30
        )
        
        print("\n=== SUCCESS ===")
        print("Response from OpenAI:")
        print(response)
        return True
        
    except Exception as e:
        print("\n=== ERROR ===")
        print(f"API call failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_direct_openai()
    sys.exit(0 if success else 1)
