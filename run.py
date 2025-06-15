"""
This script handles the setup and execution of the web application.
"""
print("--- run.py started ---")
import os
from pathlib import Path
import shutil

from dotenv import load_dotenv

# Load environment variables
env_path = Path('.env')
env_example_path = Path('.env.example')

# If .env doesn't exist, create it from example
if not env_path.exists() and env_example_path.exists():
    shutil.copy(env_example_path, env_path)
    print("Created .env file from .env.example. Please update your API keys before proceeding.")

# Load environment vars
load_dotenv()
print("--- dotenv loaded ---")

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment variables.")
    print("Please set your API key in the .env file before running the application.")
    exit(1)

# Create necessary directories
os.makedirs("vector_db", exist_ok=True)
os.makedirs("learning_paths", exist_ok=True)
print("--- API key checked and dirs created ---")

# Import and run Flask app
from web_app.app import app
print("--- web_app.app imported ---")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    print(f"Starting AI Learning Path Generator on port {port}")
    print("Visit http://localhost:5000 in your browser")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
