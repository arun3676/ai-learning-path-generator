"""
Setup script for the AI Learning Path Generator.
"""
from setuptools import setup, find_packages

setup(
    name="ai-learning-path-generator",
    version="1.0.0",
    description="An intelligent system that generates personalized learning paths using AI",
    author="AI Learning Path Generator Team",
    packages=find_packages(),
    install_requires=[
        "python-dotenv>=1.0.0",
        "Flask>=2.0.1",
        "langchain>=0.0.267",
        "langchain-openai>=0.0.1",
        "openai>=1.0.0",
        "chromadb>=0.4.13",
        "sentence-transformers>=2.2.2",
        "scikit-learn>=1.2.2",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "flask-wtf>=1.0.0",
        "Jinja2>=3.0.1",
        "werkzeug>=2.0.1",
    ],
    python_requires=">=3.8",
)
