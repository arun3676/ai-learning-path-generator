import os
import sys
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ml.model_orchestrator import ModelOrchestrator

app = Flask(__name__)
load_dotenv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_path():
    user_data = {
        'topic': request.form.get('topic'),
        'level': request.form.get('level')
    }
    
    orchestrator = ModelOrchestrator()
    path = orchestrator.generate_enhanced_path(user_data)
    
    if path:
        return render_template('learning_path.html', path=path)
    else:
        return render_template('index.html', error="Failed to generate learning path. Please try again.")

if __name__ == '__main__':
    app.run(debug=True)