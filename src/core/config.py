import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Settings:
    """Centralized configuration for EchoGrid."""
    
    # Optional API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    SEARXNG_URL: str = os.getenv("SEARXNG_URL", "http://localhost:8080")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemma3:latest")
    ROUTING_THRESHOLD: float = float(os.getenv("ROUTING_THRESHOLD", "0.1"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
