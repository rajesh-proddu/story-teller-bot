"""
Audio input/output handler for Story Teller Bot.
Handles recording audio from microphone and playing back audio.
"""
import threading
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass

import sounddevice as sd
import soundfile as sf
import numpy as np
import pyttsx3
from loguru import logger

from config.settings import settings


@dataclass
class AudioConfig:
    """Audio configuration."""

    sample_rate: int = settings.SAMPLE_RATE
    channels: int = settings.CHANNELS
    duration: int = settings.AUDIO_DURATION_SECONDS


class AudioInputHandler:
    """Handles audio input from microphone."""

    def __init__(self, config: Optional[AudioConfig] = None):
        """Initialize audio input handler.

        Args:
            config: Audio configuration.
        """
        self.config = config or AudioConfig()
        self.recording: Optional[np.ndarray] = None
        self.is_recording = False
        self.stream: Optional[sd.InputStream] = None

    def record_audio(self, duration: Optional[int] = None, on_complete: Optional[Callable] = None) -> np.ndarray:
        """Record audio from microphone.

        Args:
            duration: Recording duration in seconds.
            on_complete: Callback function when recording completes.

        Returns:
            Audio data as numpy array.
        """
        duration = duration or self.config.duration
        logger.info(f"Starting audio recording for {duration} seconds...")

        try:
            self.is_recording = True
            self.recording = sd.rec(
                int(duration * self.config.sample_rate),
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                dtype=np.float32,
            )
            sd.wait()
            self.is_recording = False

            logger.info("Recording completed successfully.")
            if on_complete:
                on_complete()

            return self.recording

        except Exception as e:
            logger.error(f"Error during audio recording: {e}")
            self.is_recording = False
            raise

    def save_audio(self, filename: Path, audio_data: Optional[np.ndarray] = None) -> Path:
        """Save recorded audio to file.

        Args:
            filename: Output filename.
            audio_data: Audio data to save (uses last recording if not provided).

        Returns:
            Path to saved audio file.
        """
        audio_data = audio_data if audio_data is not None else self.recording

        if audio_data is None:
            raise ValueError("No audio data to save. Record audio first.")

        try:
            sf.write(filename, audio_data, self.config.sample_rate)
            logger.info(f"Audio saved to {filename}")
            return Path(filename)

        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            raise

    def stop_recording(self) -> None:
        """Stop the current recording."""
        if self.is_recording:
            self.is_recording = False
            logger.info("Recording stopped.")


class AudioOutputHandler:
    """Handles audio output and text-to-speech."""

    def __init__(self):
        """Initialize audio output handler."""
        self.engine = pyttsx3.init()
        self.is_playing = False
        self.playback_thread: Optional[threading.Thread] = None
        self._setup_tts_engine()

    def _setup_tts_engine(self) -> None:
        """Setup text-to-speech engine."""
        self.engine.setProperty("rate", 150)  # Speech rate
        self.engine.setProperty("volume", 0.9)  # Volume (0.0 to 1.0)

    def speak(self, text: str, save_to_file: Optional[Path] = None) -> None:
        """Convert text to speech and play it.

        Args:
            text: Text to speak.
            save_to_file: Optional path to save audio file.
        """
        try:
            logger.info(f"Speaking text: {text[:100]}...")

            if save_to_file:
                self.engine.save_to_file(text, str(save_to_file))
                logger.info(f"Audio saved to {save_to_file}")

            self.is_playing = True
            self.engine.runAndWait()
            self.is_playing = False

        except Exception as e:
            logger.error(f"Error during text-to-speech: {e}")
            raise

    def play_audio(self, audio_file: Path) -> None:
        """Play audio file.

        Args:
            audio_file: Path to audio file.
        """
        try:
            logger.info(f"Playing audio: {audio_file}")
            audio_data, sample_rate = sf.read(audio_file)

            self.is_playing = True
            sd.play(audio_data, sample_rate)
            sd.wait()
            self.is_playing = False

            logger.info("Playback completed.")

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            raise

    def pause_playback(self) -> None:
        """Pause playback."""
        if self.is_playing:
            sd.stop()
            logger.info("Playback paused.")

    def resume_playback(self) -> None:
        """Resume playback (not supported by pyttsx3, would need reimplement)."""
        logger.warning("Resume not fully supported. Please replay from beginning.")

    def stop_playback(self) -> None:
        """Stop playback."""
        if self.is_playing:
            sd.stop()
            self.engine.stop()
            self.is_playing = False
            logger.info("Playback stopped.")
