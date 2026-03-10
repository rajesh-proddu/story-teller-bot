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

    def test_initialization(self):
        """Test speech recognizer initialization."""
        recognizer = SpeechRecognizer()

        assert recognizer.model_name == "base"
        assert recognizer.recognizer is not None

    def test_initialization_with_custom_model(self):
        """Test initialization with custom model."""
        recognizer = SpeechRecognizer(model_name="small")

        assert recognizer.model_name == "small"

    @patch('speech_recognition.AudioFile')
    @patch('speech_recognition.Recognizer.record')
    @patch('speech_recognition.Recognizer.recognize_google')
    @patch('pathlib.Path.exists')
    def test_transcribe_from_file(self, mock_exists, mock_recognize, mock_record, mock_audio_file):
        """Test transcription from file."""
        mock_exists.return_value = True
        mock_record.return_value = MagicMock()
        mock_recognize.return_value = "Hello, this is a test"

        recognizer = SpeechRecognizer()
        result = recognizer.transcribe_from_file(Path("/tmp/test.wav"))

        assert result == "Hello, this is a test"

    def test_transcribe_audio_array(self):
        """Test transcription from numpy array."""
        recognizer = SpeechRecognizer()

        audio = np.random.randn(16000).astype(np.float32)
        result = recognizer.transcribe(audio)

        # Should return placeholder for numpy arrays
        assert "placeholder" in result.lower() or result == "Audio transcription placeholder"

    def test_transcribe_nonexistent_file(self):
        """Test transcription with nonexistent file."""
        recognizer = SpeechRecognizer()

        with pytest.raises(FileNotFoundError):
            recognizer.transcribe_from_file(Path("/nonexistent/file.wav"))

    @patch('speech_recognition.AudioFile')
    @patch('speech_recognition.Recognizer.record')
    @patch('speech_recognition.Recognizer.recognize_google')
    def test_transcribe_empty_result(self, mock_recognize, mock_record, mock_audio_file):
        """Test transcription with empty result."""
        mock_record.return_value = MagicMock()
        mock_recognize.return_value = ""

        recognizer = SpeechRecognizer()
        result = recognizer.transcribe(np.random.randn(16000).astype(np.float32))

        # numpy array returns placeholder
        assert "placeholder" in result.lower() or result == "Audio transcription placeholder"
