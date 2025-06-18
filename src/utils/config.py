"""
Configuration utilities for the AI Learning Path Generator.
Loads environment variables and provides configuration settings across the application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Load environment variables from .env file, expecting it at project root (2 levels up from this file).
# This ensures changes in .env are picked up correctly.
dotenv_path = Path(__file__).resolve().parents[2] / '.env'
if dotenv_path.is_file():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"--- Successfully loaded .env from: {dotenv_path} ---")
else:
    # Fallback to default python-dotenv behavior (searches current dir and parents)
    # This can be helpful if the script is run from an unexpected location.
    print(f"--- .env not found at {dotenv_path}, attempting default load_dotenv() search. ---")
    loaded_by_default = load_dotenv()
    if loaded_by_default:
        print(f"--- Successfully loaded .env from default location (e.g., {os.getcwd()}/.env or parent). ---")
    else:
        print("--- WARNING: .env file not found by explicit path or default search. Environment variables may not be set. ---")

# Development mode flag - checked before raising key errors
DEV_MODE = os.getenv('DEV_MODE', 'False').lower() == 'true'

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# Ensure at least one API key is available (unless in DEV_MODE)
if not DEV_MODE and not any([OPENAI_API_KEY, DEEPSEEK_API_KEY, PERPLEXITY_API_KEY]):
    raise EnvironmentError("No valid AI provider API key found. Please set OPENAI_API_KEY, DEEPSEEK_API_KEY, or PERPLEXITY_API_KEY in your environment.")

# Default model provider (can be 'openai' or 'deepseek')
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "openai").lower()

# Model configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Perplexity model (see https://docs.perplexity.ai/guides/model-cards)
# Default to the lightweight online model; can be overridden via the PERPLEXITY_MODEL env var.
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "pplx-7b-online")

# Vector database settings
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db")

# Region settings
DEFAULT_REGION = os.getenv("DEFAULT_REGION", "North America")

# Web app settings
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
PORT = int(os.getenv("PORT", "5000"))

# Learning paths configuration
LEARNING_STYLES = {
    "visual": "Learns best through images, diagrams, and spatial understanding",
    "auditory": "Learns best through listening and speaking",
    "reading": "Learns best through written materials and note-taking",
    "kinesthetic": "Learns best through hands-on activities and physical interaction"
}

EXPERTISE_LEVELS = {
    "beginner": "No prior knowledge in the subject",
    "intermediate": "Some familiarity with basic concepts",
    "advanced": "Solid understanding of core principles",
    "expert": "Deep knowledge and specialization"
}

TIME_COMMITMENTS = {
    "minimal": "1-2 hours per week",
    "moderate": "3-5 hours per week",
    "substantial": "6-10 hours per week",
    "intensive": "10+ hours per week"
}

# Resource types with weights for learning styles (higher = more relevant)
RESOURCE_TYPES = {
    "video": {"visual": 5, "auditory": 4, "reading": 2, "kinesthetic": 3},
    "article": {"visual": 3, "reading": 5, "auditory": 2, "kinesthetic": 1},
    "book": {"reading": 5, "visual": 3, "auditory": 2, "kinesthetic": 1},
    "interactive": {"kinesthetic": 5, "visual": 4, "auditory": 3, "reading": 3},
    "course": {"visual": 4, "auditory": 4, "reading": 4, "kinesthetic": 3},
    "documentation": {"reading": 5, "visual": 3, "auditory": 1, "kinesthetic": 1},
    "podcast": {"auditory": 5, "reading": 2, "visual": 1, "kinesthetic": 1},
    "project": {"kinesthetic": 5, "visual": 3, "reading": 3, "auditory": 2}
}
