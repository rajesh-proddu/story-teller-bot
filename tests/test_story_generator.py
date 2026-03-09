"""
Unit tests for story generator module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.story_generator import StoryGenerator


class TestStoryGenerator:
    """Test StoryGenerator class."""
    
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModelForCausalLM.from_pretrained')
    @patch('transformers.pipeline')
    def test_initialization(self, mock_pipeline, mock_model, mock_tokenizer):
        """Test story generator initialization."""
        with patch.object(StoryGenerator, '_init_model'):
            generator = StoryGenerator()
            assert generator.model_name == "gpt2"
    
    def test_extract_objects_single_object(self):
        """Test extracting single object from text."""
        generator = StoryGenerator.__new__(StoryGenerator)
        
        text = "I want a story with a king"
        objects = generator.extract_objects(text)
        
        assert "king" in objects
    
    def test_extract_objects_multiple_objects(self):
        """Test extracting multiple objects from text."""
        generator = StoryGenerator.__new__(StoryGenerator)
        
        text = "I want a story with a king and a lion in a forest"
        objects = generator.extract_objects(text)
        
        assert "king" in objects
        assert "lion" in objects
        assert "forest" in objects
    
    def test_extract_objects_removes_filler_words(self):
        """Test that filler words are removed."""
        generator = StoryGenerator.__new__(StoryGenerator)
        
        text = "I want a story with a king"
        objects = generator.extract_objects(text)
        
        # Should not contain filler words
        assert all(word not in ["i", "want", "story", "with", "a"] for word in objects)
    
    def test_extract_objects_empty_input(self):
        """Test extracting objects from empty input."""
        generator = StoryGenerator.__new__(StoryGenerator)
        
        text = ""
        objects = generator.extract_objects(text)
        
        assert len(objects) == 0
    
    def test_create_prompt(self):
        """Test prompt creation."""
        generator = StoryGenerator.__new__(StoryGenerator)
        
        prompt = generator._create_prompt("king, lion")
        
        assert isinstance(prompt, str)
        assert "king" in prompt
        assert "lion" in prompt
        assert len(prompt) > 0
    
    def test_clean_story(self):
        """Test story cleaning."""
        generator = StoryGenerator.__new__(StoryGenerator)
        
        prompt = "Once upon a time"
        raw_story = f"{prompt} there lived a king. He was wise."
        
        cleaned = generator._clean_story(raw_story, prompt)
        
        assert "Once upon a time" not in cleaned or len(cleaned) > 0
        assert "wise" in cleaned
    
    def test_generate_story_from_input_with_objects(self):
        """Test story generation from text input."""
        generator = StoryGenerator.__new__(StoryGenerator)
        generator.extract_objects = Mock(return_value=["king", "lion"])
        generator.generate_story = Mock(return_value="Once upon a time...")
        
        story = generator.generate_story_from_input("I want a story with a king and lion")
        
        assert story == "Once upon a time..."
        generator.extract_objects.assert_called_once()
        generator.generate_story.assert_called_once()
    
    def test_generate_story_from_input_no_objects(self):
        """Test story generation when no objects extracted."""
        generator = StoryGenerator.__new__(StoryGenerator)
        generator.extract_objects = Mock(return_value=[])
        generator.generate_story = Mock(return_value="A default story")
        
        story = generator.generate_story_from_input("")
        
        assert story == "A default story"
        # Should use default objects
        assert len(generator.generate_story.call_args[0][0]) > 0
