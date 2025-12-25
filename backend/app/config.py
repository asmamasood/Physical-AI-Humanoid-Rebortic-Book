"""
Configuration management for RAG Chatboard backend.

Loads settings from environment variables with validation.
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Explicitly load .env from the root directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
print(f"DEBUG: Loading .env from {env_path}")
load_dotenv(env_path)

print(f"DEBUG: QDRANT_COLLECTION in os.environ: {os.environ.get('QDRANT_COLLECTION')}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Embedding Configuration
    embedding_provider: str = Field(default="local", alias="EMBEDDING_PROVIDER")  # "local" or "cohere"
    
    # Cohere API (Embeddings)
    cohere_api_key: Optional[str] = Field(default=None, alias="COHERE_API_KEY")
    
    # Qdrant Cloud (Vector Database)
    qdrant_url: str = Field(..., alias="QDRANT_URL")
    qdrant_api_key: str = Field(..., alias="QDRANT_API_KEY")
    qdrant_collection: str = Field(default="book_v1_local", alias="QDRANT_COLLECTION")
    
    # Gemini API (LLM)
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    gemini_model_name: str = Field(default="models/gemini-flash-latest", alias="GEMINI_MODEL_NAME")
    
    # Admin Authentication
    admin_secret: str = Field(..., alias="ADMIN_SECRET")
    
    # Neon Database (Optional)
    neon_db_url: Optional[str] = Field(default=None, alias="NEON_DB_URL")
    
    # CORS
    cors_origins: str = Field(
        default="https://asmamasood.github.io,http://localhost:3000",
        alias="CORS_ORIGINS"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    
    # RAG Settings
    score_threshold: float = Field(default=0.30, alias="SCORE_THRESHOLD")
    
    # Docs Path (for ingestion)
    docs_path: str = Field(
        default="physical-ai-robotics-book/docs",
        alias="DOCS_PATH"
    )

    # Chunking Configuration
    chunk_min_tokens: int = Field(default=200, alias="CHUNK_MIN_TOKENS")
    chunk_max_tokens: int = Field(default=800, alias="CHUNK_MAX_TOKENS")
    chunk_overlap_sentences: int = Field(default=2, alias="CHUNK_OVERLAP_SENTENCES")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# @lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to avoid reloading on every request.
    """
    return Settings()


def validate_settings() -> List[str]:
    """
    Validate that all required settings are configured.
    
    Returns list of error messages (empty if valid).
    """
    errors = []
    
    try:
        settings = get_settings()
        
        # Check each required field
        if not settings.cohere_api_key:
            errors.append("COHERE_API_KEY is not set")
        if not settings.qdrant_url:
            errors.append("QDRANT_URL is not set")
        if not settings.qdrant_api_key:
            errors.append("QDRANT_API_KEY is not set")
        if not settings.gemini_api_key:
            errors.append("GEMINI_API_KEY is not set")
        if not settings.admin_secret:
            errors.append("ADMIN_SECRET is not set")
            
    except Exception as e:
        errors.append(f"Configuration error: {str(e)}")
    
    return errors
