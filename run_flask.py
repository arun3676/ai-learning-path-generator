import os
import sys

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Import the app factory
from web_app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
