#!/usr/bin/env python
# A simple script to test if the OpenAI API key works correctly

import os
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

# Get the API key
api_key = os.getenv('OPENAI_API_KEY')

print(f"Loaded API key (first 10 chars): {api_key[:10]}...")

# Test the API key with a simple request
try:
    from openai import OpenAI
    
    # Initialize the client with the API key
    client = OpenAI(api_key=api_key)
    
    # Make a simple test request
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello world!"}
        ],
        max_tokens=10
    )
    
    # Print the response
    print(f"API test successful! Response: {response.choices[0].message.content}")
    print("Your API key is valid.")
    
except Exception as e:
    print(f"Error testing API key: {str(e)}")
    print("If this is an authentication error, your API key might be invalid or in the wrong format.")
    sys.exit(1)
