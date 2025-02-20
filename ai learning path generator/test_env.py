# Create a test_env.py file in your root directory
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"First few characters of API key: {api_key[:7] if api_key else 'None'}")