import os
import sys

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Import the app factory
import os
from web_app import create_app

# Set DEV_MODE=True in .env to bypass API key checks
DEV_MODE = os.environ.get('DEV_MODE', 'False').lower() == 'true'

if DEV_MODE:
    print("\033[93m⚠️  Running in DEV_MODE - API calls will be stubbed!\033[0m")
    os.environ['FLASK_ENV'] = 'development'

app = create_app()

if __name__ == "__main__":
    print("Starting Flask application...")
    app.run(debug=True, port=5000)
