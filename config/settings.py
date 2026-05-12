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
    AUDIO_DURATION_SECONDS: int = 15  # Max recording duration
    CHANNELS: int = 1  # Mono
    

    # Model settings
    # WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    # TEXT_GENERATION_MODEL: str = "gpt2"  # Using open-source model
    # TTS_ENGINE: str = "pyttsx3"  # Text-to-speech engine
    
    # # Story generation settings
    # MAX_STORY_LENGTH: int = 500  # Max words in story
    # TEMPERATURE: float = 0.7
    # TOP_P: float = 0.9
    
    # Much better accuracy for voice-to-text
    WHISPER_MODEL: str = "small"  # 'small' is the sweet spot for CPU

    # GPT-2 is very old; TinyLlama or Phi-2 are modern and much smarter
    TEXT_GENERATION_MODEL: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0" 
    TTS_ENGINE: str = "pyttsx3"  # Using pyttsx3 for offline TTS

    MAX_STORY_LENGTH: int = 250  # Keep it concise for better quality
    TEMPERATURE: float = 0.8     # Slightly higher for more creative wording
    TOP_P: float = 0.95          # Look at more word options

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
