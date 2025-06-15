"""
Flask web application for the AI Learning Path Generator.
This file is now minimal. Core application logic is in the app factory (`web_app/__init__.py`)
and blueprints (`web_app/main_routes.py`, `web_app/auth_routes.py`, etc.).
"""
print("--- web_app/app.py execution started (minimal) ---")
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to sys.path to allow imports from src, etc.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
print(f"PROJECT_ROOT ({PROJECT_ROOT}) added to sys.path.")

# Load environment variables. This is useful if this script is run directly
# or if FLASK_APP points here, though run_flask.py is the preferred entry point.
dotenv_path = Path(__file__).parents[1] / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print(f"Loaded .env file from: {dotenv_path}")
    # Optional: Confirm API key loading for quick diagnostics
    # api_key = os.getenv('OPENAI_API_KEY')
    # if api_key and api_key.startswith("sk-"):
    #     print("OpenAI API key appears to be loaded.")
    # else:
    #     print("WARNING: OpenAI API key not found or seems invalid after .env load.")
else:
    print(f"INFO: .env file not found at {dotenv_path}. Relying on system environment variables.")

print("--- web_app/app.py execution finished (minimal) ---")

# The main application is now created and run via the app factory in __init__.py
# and typically started with run_flask.py.
# If you need to run a very simple, standalone Flask app from this file for testing,
# you would instantiate Flask here, define routes, and run it:
#
# from flask import Flask
# if __name__ == '__main__':
#     basic_app = Flask(__name__)
#     @basic_app.route('/test_app_py')
#     def _test_route():
#         return "Minimal app.py test route is working!"
#     print("Starting minimal Flask app from app.py on port 5002 (for testing only)")
#     basic_app.run(port=5002, debug=True)
