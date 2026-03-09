"""
Speech recognition module for Story Teller Bot.
Converts audio to text using Whisper model from OpenAI.
"""
from pathlib import Path
from typing import Optional

import whisper
import numpy as np
from loguru import logger

from config.settings import settings


class SpeechRecognizer:
    """Speech recognition using Whisper model."""
    
    def __init__(self, model_name: str = settings.WHISPER_MODEL):
        """Initialize speech recognizer.
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large).
        """
        self.model_name = model_name
        self.model: Optional[whisper.Whisper] = None
        self._load_model()
        
    def _load_model(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(
                self.model_name,
                device="cpu"  # Use CPU for local machine
            )
            logger.info(f"Whisper model loaded successfully.")
            
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe(
        self,
        audio_input: Path | np.ndarray | str,
        language: str = "en"
    ) -> str:
        """Transcribe audio to text.
        
        Args:
            audio_input: Path to audio file, numpy array, or URL.
            language: Language code (default: English).
            
        Returns:
            Transcribed text.
        """
        try:
            logger.info("Starting audio transcription...")
            
            result = self.model.transcribe(
                audio_input,
                language=language,
                fp16=False  # Use fp32 for CPU stability
            )
            
            text = result.get("text", "").strip()
            logger.info(f"Transcription completed: {text[:100]}...")
            
            return text
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def transcribe_from_file(self, audio_file: Path) -> str:
        """Transcribe audio from file.
        
        Args:
            audio_file: Path to audio file.
            
        Returns:
            Transcribed text.
        """
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        return self.transcribe(str(audio_file))
