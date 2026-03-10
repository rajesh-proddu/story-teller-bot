"""
Configuration module for Story Teller Bot.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    MODELS_CACHE_DIR: Path = PROJECT_ROOT / "models_cache"
    AUDIO_OUTPUT_DIR: Path = PROJECT_ROOT / "audio_output"
    
    # Audio settings
    SAMPLE_RATE: int = 16000
    AUDIO_DURATION_SECONDS: int = 30  # Max recording duration
    CHANNELS: int = 1  # Mono
    
    # Model settings
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    TEXT_GENERATION_MODEL: str = "gpt2"  # Using open-source model
    TTS_ENGINE: str = "pyttsx3"  # Text-to-speech engine
    
    # Story generation settings
    MAX_STORY_LENGTH: int = 500  # Max words in story
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # API settings
    ENABLE_API: bool = False
    API_PORT: int = 8000
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
    
    def __post_init__(self) -> None:
        """Create required directories."""
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
