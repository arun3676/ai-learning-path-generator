# AI Learning Path Generator 🎓

An intelligent system that generates personalized learning paths using AI, built with Python, LangChain, and ML technologies.

## Overview
This project uses AI to create customized learning paths based on:
- Topic selection
- User's expertise level
- Learning style preferences
- Time availability

## Features
- 🤖 AI-powered path generation
- 📊 Difficulty assessment
- 📈 Progress tracking
- 🌐 Interactive web interface
- 📚 Resource recommendations

## Tech Stack
- **AI/ML**: LangChain, OpenAI, SentenceTransformers
- **Database**: ChromaDB for vector storage
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS (Tailwind)

## Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation
```bash
ai_learning_path_generator/
├── src/
│   ├── core/
│   │   ├── init.py
│   │   ├── analytics.py
│   │   ├── knowledge_graph.py
│   │   ├── learning_path.py
│   │   ├── path_optimization.py
│   │   └── progress_tracker.py
│   ├── advanced/
│   ├── ml/
│   ├── utils/
│   ├── agent.py
│   ├── embeddings.py
│   ├── init.py
│   ├── learning_path.py
│   └── retriever.py
├── web_app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── learning_path.html
│   └── app.py
├── tests/
│   ├── test_advanced_features.py
│   ├── test_agent.py
│   ├── test_embeddings.py
│   ├── test_env.py
│   ├── test_formatted_path.py
│   ├── test_learning_path.py
│   ├── test_ml_models.py
│   └── test_retriever.py

# Running the Application and Testing

## Web Interface Setup
```bash
cd web_app
python app.py
Visit http://localhost:5000 in your browser
Running Tests
bashCopy# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_learning_path.py
Using the App
Web Interface

Select your learning topic
Choose your experience level
Get personalized learning path with:

Prerequisites
Learning modules
Time estimates
Resource links



API Usage
pythonCopyfrom src.core.learning_path import LearningPathGenerator

# Initialize generator
generator = LearningPathGenerator(api_key="your-openai-api-key")

# Generate learning path
path = generator.generate_learning_path(
    topic="Machine Learning",
    user_level="intermediate"
)
Key Features

🤖 AI-powered path generation using LangChain and GPT
📊 Difficulty assessment and progress tracking
🔍 Vector-based content retrieval using ChromaDB
📈 Learning analytics and visualizations
🌐 Interactive web interface

Built With

LangChain & OpenAI
ChromaDB
Python & Flask
HTML & Tailwind CSS

License
MIT
Contact
Your Name - your.email@example.com
Acknowledgments

OpenAI for GPT API
LangChain framework
ChromaDB for vector storage



📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
📧 Contact
Arun Kumar Chukkala - arunkiran721@gmail.com
Project Link: https://github.com/arun3676/ai-learning-path-generator
