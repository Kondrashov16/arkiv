# core/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# It's good practice to call this early in your application's lifecycle.
# If main.py imports something that imports config, it will be loaded.
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

class Settings:
    """
    Application settings loaded from environment variables.
    """
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL_NAME: str = os.getenv("OPENROUTER_MODEL_NAME", "mistralai/mistral-7b-instruct")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Maximum number of relevant chunks to retrieve for context
    MAX_CONTEXT_CHUNKS: int = int(os.getenv("MAX_CONTEXT_CHUNKS", 5))
    
    # Text chunking parameters
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 500)) # Number of tokens
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50)) # Number of tokens

    # Directory to store uploaded files temporarily
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "uploads")

    def __init__(self):
        """
        Validate essential settings upon initialization.
        """
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY must be set in the .env file.")
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

# Instantiate settings to be imported by other modules
settings = Settings()

if __name__ == '__main__':
    # For testing if settings are loaded correctly
    print(f"OpenRouter API Key Loaded: {'Yes' if settings.OPENROUTER_API_KEY else 'No'}")
    print(f"OpenRouter Model Name: {settings.OPENROUTER_MODEL_NAME}")
    print(f"Embedding Model Name: {settings.EMBEDDING_MODEL_NAME}")
    print(f"Max Context Chunks: {settings.MAX_CONTEXT_CHUNKS}")
    print(f"Chunk Size: {settings.CHUNK_SIZE}")
    print(f"Chunk Overlap: {settings.CHUNK_OVERLAP}")
    print(f"Upload Directory: {settings.UPLOAD_DIR}")

