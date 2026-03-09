"""
Unit tests for speech recognizer module.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from src.speech_recognizer import SpeechRecognizer


class TestSpeechRecognizer:
    """Test SpeechRecognizer class."""
    
    @patch('whisper.load_model')
    def test_initialization(self, mock_load):
        """Test speech recognizer initialization."""
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        recognizer = SpeechRecognizer()
        
        assert recognizer.model_name == "base"
        assert recognizer.model is not None
        mock_load.assert_called_once()
    
    @patch('whisper.load_model')
    def test_initialization_with_custom_model(self, mock_load):
        """Test initialization with custom model."""
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        recognizer = SpeechRecognizer(model_name="small")
        
        assert recognizer.model_name == "small"
        mock_load.assert_called_once_with("small", device="cpu")
    
    @patch('whisper.load_model')
    def test_transcribe_from_file(self, mock_load):
        """Test transcription from file."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Hello, this is a test"}
        mock_load.return_value = mock_model
        
        recognizer = SpeechRecognizer()
        recognizer.model = mock_model
        
        result = recognizer.transcribe_from_file(Path("/tmp/test.wav"))
        
        assert result == "Hello, this is a test"
        mock_model.transcribe.assert_called_once()
    
    @patch('whisper.load_model')
    def test_transcribe_audio_array(self, mock_load):
        """Test transcription from numpy array."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Test transcription"}
        mock_load.return_value = mock_model
        
        recognizer = SpeechRecognizer()
        recognizer.model = mock_model
        
        audio = np.random.randn(16000).astype(np.float32)
        result = recognizer.transcribe(audio)
        
        assert result == "Test transcription"
    
    @patch('whisper.load_model')
    def test_transcribe_nonexistent_file(self, mock_load):
        """Test transcription with nonexistent file."""
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        recognizer = SpeechRecognizer()
        
        with pytest.raises(FileNotFoundError):
            recognizer.transcribe_from_file(Path("/nonexistent/file.wav"))
    
    @patch('whisper.load_model')
    def test_transcribe_empty_result(self, mock_load):
        """Test transcription with empty result."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": ""}
        mock_load.return_value = mock_model
        
        recognizer = SpeechRecognizer()
        recognizer.model = mock_model
        
        result = recognizer.transcribe(np.random.randn(16000).astype(np.float32))
        
        assert result == ""
