"""
Configuration settings for the application.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path
from typing import ClassVar


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    PROJECT_ROOT: ClassVar[str] = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../.."
        )
    )

    # App
    APP_NAME: str = "intelligent-rec-rag"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "info"
    
    # API
    API_TITLE: str = "RAG Powered Recommendation Engine"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # Database
    # MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_URL: str = "mongodb+srv://bhavesh:bhavesh@cluster0.vrlh5wh.mongodb.net/"
    DATABASE_NAME: str = "recommendation_engine"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # ML / RAG
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "./artifacts/vector_store"
    CHROMA_PERSIST_DIR: str = "./artifacts/chroma"
    TFIDF_VECTORIZER_PATH: str = "./artifacts/tfidf_vectorizer.pkl"
    ITEM_FEATURES_PATH: str = "./data/processed/item_features.npz"
    ITEM_FEATURES_INDEX_PATH: str = "./data/processed/item_features_index.csv"
    USER_ITEM_MATRIX_PATH: str = "./data/processed/user_item_matrix.npz"
    ITEM_TO_INDEX_PATH: str = os.path.join(
        PROJECT_ROOT,
        "ml",
        "artifacts",
        "item_to_index.pkl"
    )

    INDEX_TO_ITEM_PATH: str = os.path.join(
        PROJECT_ROOT,
        "ml",
        "artifacts",
        "index_to_item.pkl"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False




@lru_cache()
def get_settings():
    """Get cached settings instance."""
    return Settings()
