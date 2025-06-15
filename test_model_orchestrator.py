import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Load environment variables
load_dotenv()

print("Testing ModelOrchestrator...")
try:
    from src.ml.model_orchestrator import ModelOrchestrator
    print("Successfully imported ModelOrchestrator")
    
    # Initialize with API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
    else:
        print(f"Using API key starting with: {api_key[:10]}...")
        
        try:
            orchestrator = ModelOrchestrator(api_key=api_key)
            print("Successfully initialized ModelOrchestrator")
        except Exception as e:
            print(f"Error initializing ModelOrchestrator: {e}")
            import traceback
            traceback.print_exc()
except ImportError as e:
    print(f"Error importing ModelOrchestrator: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("Test script finished.")
