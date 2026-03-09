"""
Unit tests for the main bot module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.bot import StoryTellerBot, BotState


class TestBotState:
    """Test BotState enum."""
    
    def test_bot_states_exist(self):
        """Test that all required bot states exist."""
        assert BotState.IDLE.value == "idle"
        assert BotState.LISTENING.value == "listening"
        assert BotState.PROCESSING.value == "processing"
        assert BotState.SPEAKING.value == "speaking"
        assert BotState.PAUSED.value == "paused"
        assert BotState.STOPPED.value == "stopped"


class TestStoryTellerBot:
    """Test StoryTellerBot class."""
    
    @patch('src.bot.AudioInputHandler')
    @patch('src.bot.AudioOutputHandler')
    @patch('src.bot.SpeechRecognizer')
    @patch('src.bot.StoryGenerator')
    def test_initialization(self, mock_generator, mock_recognizer, mock_output, mock_input):
        """Test bot initialization."""
        bot = StoryTellerBot()
        
        assert bot.state == BotState.IDLE
        assert bot.current_story is None
        assert bot.current_story_file is None
    
    @patch('src.bot.AudioInputHandler')
    @patch('src.bot.AudioOutputHandler')
    @patch('src.bot.SpeechRecognizer')
    @patch('src.bot.StoryGenerator')
    def test_state_transitions(self, mock_generator, mock_recognizer, mock_output, mock_input):
        """Test bot state transitions."""
        bot = StoryTellerBot()
        
        # Start in idle state
        assert bot.state == BotState.IDLE
        
        # Transition to listening
        bot.state = BotState.LISTENING
        assert bot.state == BotState.LISTENING
        
        # Transition to processing
        bot.state = BotState.PROCESSING
        assert bot.state == BotState.PROCESSING
        
        # Transition to speaking
        bot.state = BotState.SPEAKING
        assert bot.state == BotState.SPEAKING
        
        # Transition back to idle
        bot.state = BotState.IDLE
        assert bot.state == BotState.IDLE
