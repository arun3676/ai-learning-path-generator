import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv()

print("=== Starting Minimal Test ===")

# Test basic Python environment
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Project root:", PROJECT_ROOT)

# Test environment variables
api_key = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY exists:", bool(api_key))
if api_key:
    print("API key starts with:", api_key[:5] + "...")

# Test basic imports
try:
    import pydantic
    print(f"Pydantic version: {pydantic.__version__}")
except ImportError as e:
    print(f"Pydantic import error: {e}")

try:
    from langchain_openai import OpenAI
    print("Successfully imported langchain_openai")
except ImportError as e:
    print(f"langchain_openai import error: {e}")

print("=== Test Completed ===")
