"""
Unit tests for audio handler module.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.audio_handler import AudioInputHandler, AudioOutputHandler, AudioConfig
from config.settings import settings


class TestAudioConfig:
    """Test AudioConfig dataclass."""
    
    def test_default_audio_config(self):
        """Test default configuration."""
        config = AudioConfig()
        assert config.sample_rate == settings.SAMPLE_RATE
        assert config.channels == settings.CHANNELS
        assert config.duration == settings.AUDIO_DURATION_SECONDS
    
    def test_custom_audio_config(self):
        """Test custom configuration."""
        config = AudioConfig(sample_rate=44100, channels=2, duration=60)
        assert config.sample_rate == 44100
        assert config.channels == 2
        assert config.duration == 60


class TestAudioInputHandler:
    """Test AudioInputHandler class."""
    
    def test_initialization(self):
        """Test handler initialization."""
        handler = AudioInputHandler()
        assert handler.is_recording is False
        assert handler.recording is None
    
    @patch('sounddevice.rec')
    @patch('sounddevice.wait')
    def test_record_audio(self, mock_wait, mock_rec):
        """Test audio recording."""
        # Mock recording data
        mock_audio_data = np.random.randn(16000, 1).astype(np.float32)
        mock_rec.return_value = mock_audio_data
        
        handler = AudioInputHandler()
        result = handler.record_audio(duration=1)
        
        assert result is not None
        mock_rec.assert_called_once()
        mock_wait.assert_called_once()
    
    def test_save_audio(self, tmp_path):
        """Test saving audio to file."""
        handler = AudioInputHandler()
        audio_data = np.random.randn(16000, 1).astype(np.float32)
        
        output_file = tmp_path / "test_audio.wav"
        result = handler.save_audio(output_file, audio_data)
        
        assert result.exists()
        assert result == output_file
    
    def test_save_audio_without_data(self):
        """Test saving audio without data raises error."""
        handler = AudioInputHandler()
        
        with pytest.raises(ValueError):
            handler.save_audio(Path("test.wav"))


class TestAudioOutputHandler:
    """Test AudioOutputHandler class."""

    @patch('pyttsx3.init')
    def test_initialization(self, mock_engine):
        """Test handler initialization."""
        mock_tts = MagicMock()
        mock_engine.return_value = mock_tts

        handler = AudioOutputHandler()
        assert handler.is_playing is False
        assert handler.engine is not None
    
    @patch('pyttsx3.init')
    def test_speak(self, mock_engine):
        """Test text-to-speech."""
        mock_tts = MagicMock()
        mock_engine.return_value = mock_tts
        
        handler = AudioOutputHandler()
        handler.engine = mock_tts
        handler.speak("Hello, this is a test story.")
        
        mock_tts.runAndWait.assert_called_once()
    
    @patch('soundfile.read')
    @patch('sounddevice.play')
    @patch('sounddevice.wait')
    @patch('pyttsx3.init')
    def test_play_audio(self, mock_engine, mock_wait, mock_play, mock_read):
        """Test playing audio file."""
        mock_tts = MagicMock()
        mock_engine.return_value = mock_tts
        mock_audio_data = np.random.randn(16000, 1).astype(np.float32)
        mock_read.return_value = (mock_audio_data, 16000)

        handler = AudioOutputHandler()
        handler.engine = mock_tts
        handler.play_audio(Path("test.wav"))

        mock_play.assert_called_once()
        mock_wait.assert_called_once()
