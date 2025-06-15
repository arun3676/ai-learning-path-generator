# AI Learning Path Generator 🎓

An intelligent system that generates personalized learning paths using AI, built with Python, LangChain, and ML technologies.

## Overview

This project uses advanced AI techniques to create highly customized learning paths based on:
- Topic selection and expertise level
- Individual learning style preferences
- Time availability and study preferences
- Specific learning goals and objectives

The system combines OpenAI's language models with vector database technology to create detailed, personalized educational roadmaps with recommended resources, study schedules, and progress tracking.

## Features

- 🧠 **AI-powered path generation** using LangChain and OpenAI
- 🎯 **Learning style adaptation** with support for visual, auditory, reading, and kinesthetic learners
- 📊 **Difficulty assessment** of content using NLP analysis
- 📈 **Progress tracking** with milestone prediction
- 📆 **Study scheduling** with customizable time commitments
- 🔍 **Resource recommendations** tailored to learning style
- 💾 **Vector database** for efficient semantic search
- 🌐 **Interactive web interface** with modern UI/UX
- 🔄 **API endpoints** for integration with other systems

## Tech Stack

- **AI/ML**: LangChain, OpenAI, SentenceTransformers
- **Vector Database**: ChromaDB for semantic document storage
- **Backend**: Python, Flask
- **Frontend**: HTML, CSS (Tailwind)

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ai-learning-path-generator-v2.git
cd ai-learning-path-generator-v2
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up your `.env` file with the required API keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the Flask web application
```bash
python web_app/app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
ai-learning-path-generator-v2/
│
├── src/                      # Core source code
│   ├── agent.py              # AI agent implementation
│   ├── learning_path.py      # Learning path generation logic
│   ├── ml/                   # Machine learning components
│   │   ├── model_orchestrator.py  # Manages AI models
│   │   └── embeddings.py     # Vector embedding utilities
│   ├── utils/                # Utility functions
│   │   ├── config.py         # Configuration management
│   │   └── helpers.py        # Helper functions
│   └── data/                 # Data management
│       ├── document_store.py # Vector database interface
│       └── resources.py      # Educational resource handling
│
├── web_app/                  # Flask web application
│   ├── app.py                # Flask application entry point
│   ├── static/               # Static assets (CSS, JS)
│   │   ├── css/              # Tailwind and custom CSS
│   │   └── js/               # JavaScript files
│   └── templates/            # HTML templates
│       ├── index.html        # Landing page
│       ├── result.html       # Results display
│       └── components/       # Reusable UI components
│
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── LICENSE                   # License information
```

## Deployment

### 1. Local Development

```bash
# 1. Clone and enter the repo
 git clone https://github.com/<your-gh-user>/ai-learning-path-generator-v2.git
 cd ai-learning-path-generator-v2

# 2. Create a virtual environment (optional but recommended)
 python -m venv venv
 source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
 pip install -r requirements.txt

# 4. Configure environment variables
 cp .env.example .env  # then edit .env with your own keys

# 5. Launch the dev server
 python run_flask.py
```
Navigate to `http://localhost:5000`.

### 2. Production (Render.com example)

1. Push this code to a GitHub repo.
2. In Render, choose "New → Web Service" and connect the repo.
3. Render auto-detects the **Procfile** (`web: gunicorn run_flask:app`). Leave the build command blank.
4. Set environment variables in **Settings → Environment** (e.g. `OPENAI_API_KEY`, `SECRET_KEY`, `DATABASE_URL`).
5. Click **Create Web Service**. Render will install deps, build, and start Gunicorn on port 10000.
6. Once live, open the Render URL on desktop and mobile.

### 3. Manual Docker deploy

A bare-bones image can be built with:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD gunicorn run_flask:app -b 0.0.0.0:$PORT
```

Build & run:
```bash
docker build -t learning-path .
docker run -e PORT=5000 -e OPENAI_API_KEY=... -p 5000:5000 learning-path
```

### Key Files

| File | Purpose |
|------|---------|
| `Procfile` | Tells Render/Heroku to start Gunicorn |
| `requirements.txt` | All Python dependencies including `gunicorn` |
| `run_flask.py` | App entry: imports `create_app()` |
| `.env.example` | Template for your environment variables |

## License

MIT
