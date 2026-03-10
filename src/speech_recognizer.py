"""
Speech recognition module for Story Teller Bot.
Converts audio to text using SpeechRecognition library.
"""
from pathlib import Path
from typing import Optional

import speech_recognition as sr
import numpy as np
from loguru import logger

from config.settings import settings


class SpeechRecognizer:
    """Speech recognition using Google Speech Recognition."""

    def __init__(self, model_name: str = settings.WHISPER_MODEL):
        """Initialize speech recognizer.

        Args:
            model_name: Model name (kept for compatibility, not used with SpeechRecognition).
        """
        self.model_name = model_name
        self.recognizer = sr.Recognizer()
        logger.info("Speech recognizer initialized with Google Speech Recognition.")

    def _load_model(self) -> None:
        """Load model (kept for compatibility, no-op for Google SR)."""
        pass

    def transcribe(self, audio_input: Path | np.ndarray | str, language: str = "en") -> str:
        """Transcribe audio to text.

        Args:
            audio_input: Path to audio file or numpy array.
            language: Language code (default: English).

        Returns:
            Transcribed text.
        """
        try:
            logger.info("Starting audio transcription...")

            # Handle file path input
            if isinstance(audio_input, (Path, str)):
                with sr.AudioFile(str(audio_input)) as source:
                    audio = self.recognizer.record(source)
            elif isinstance(audio_input, np.ndarray):
                # Convert numpy array to audio data
                logger.warning("Direct numpy array transcription not yet implemented, using placeholder")
                return "Audio transcription placeholder"
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_input)}")

            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=language)
            logger.info(f"Transcription completed: {text[:100]}...")

            return text

        except sr.UnknownValueError:
            logger.error("Google Speech Recognition could not understand audio")
            raise
        except sr.RequestError as e:
            logger.error(f"Error with Google Speech Recognition service: {e}")
            raise
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
