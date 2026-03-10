"""
Story generation module for Story Teller Bot.
Generates creative stories based on user input objects.
"""
from typing import List
import re

from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from loguru import logger

from config.settings import settings


class StoryGenerator:
    """Generate stories based on input objects using transformers."""

    def __init__(self, model_name: str = settings.TEXT_GENERATION_MODEL):
        """Initialize story generator.

        Args:
            model_name: Model name from HuggingFace (gpt2, distilgpt2, etc).
        """
        self.model_name = model_name
        self.pipeline = None
        self.tokenizer = None
        self.model = None
        self._init_model()

    def _init_model(self) -> None:
        """Initialize the text generation model."""
        try:
            logger.info(f"Loading text generation model: {self.model_name}")

            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

            # Create pipeline
            self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device=-1)  # CPU

            logger.info(f"Model {self.model_name} loaded successfully.")

        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise

    def extract_objects(self, text: str) -> List[str]:
        """Extract objects from user input.

        Args:
            text: User input text.

        Returns:
            List of extracted objects.
        """
        # Simple extraction - look for common patterns
        # In production, could use NER (Named Entity Recognition)

        # Remove common filler words
        filler_words = {
            "a",
            "an",
            "the",
            "with",
            "in",
            "on",
            "at",
            "is",
            "are",
            "i",
            "want",
            "story",
            "please",
            "can",
            "you",
            "make",
            "tell",
            "about",
            "and",
            "or",
            "to",
            "for",
        }

        words = text.lower().split()
        objects = [word for word in words if word not in filler_words and len(word) > 2]

        logger.info(f"Extracted objects: {objects}")
        return objects

    def generate_story(
        self,
        objects: List[str],
        max_length: int = settings.MAX_STORY_LENGTH,
        temperature: float = settings.TEMPERATURE,
        top_p: float = settings.TOP_P,
    ) -> str:
        """Generate a story with given objects.

        Args:
            objects: List of objects to include in story.
            max_length: Maximum story length in words.
            temperature: Sampling temperature for generation.
            top_p: Nucleus sampling parameter.

        Returns:
            Generated story text.
        """
        try:
            # Create prompt
            objects_str = ", ".join(objects)
            prompt = self._create_prompt(objects_str)

            logger.info(f"Generating story with prompt: {prompt[:100]}...")

            # Generate story
            outputs = self.pipeline(
                prompt,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                num_return_sequences=1,
            )

            story = outputs[0]["generated_text"]

            # Clean up the story
            story = self._clean_story(story, prompt)

            logger.info(f"Story generated: {len(story.split())} words")
            return story

        except Exception as e:
            logger.error(f"Error generating story: {e}")
            raise

    def _create_prompt(self, objects: str) -> str:
        """Create a prompt for story generation.

        Args:
            objects: Objects to include in story.

        Returns:
            Story generation prompt.
        """
        prompts = [
            f"Once upon a time, there was a magical adventure with {objects}. The story begins...",
            f"In a mystical kingdom lived {objects}. One day, an incredible adventure started...",
            f"Deep in an enchanted forest, {objects} met on an extraordinary day. Here's what happened...",
        ]

        import random

        return random.choice(prompts)

    def _clean_story(self, story: str, prompt: str) -> str:
        """Clean and format the generated story.

        Args:
            story: Raw generated story.
            prompt: Original prompt.

        Returns:
            Cleaned story.
        """
        # Remove the prompt from the story
        if prompt in story:
            story = story.replace(prompt, "").strip()

        # Format paragraphs
        story = re.sub(r"\n+", "\n", story)

        # Clean up sentence fragments
        sentences = story.split(".")
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        story = ". ".join(sentences) + "."

        return story

    def generate_story_from_input(self, user_input: str) -> str:
        """Generate story from user text input.

        Args:
            user_input: User's text description of desired story.

        Returns:
            Generated story.
        """
        objects = self.extract_objects(user_input)

        if not objects:
            logger.warning("No objects extracted from input. Using default.")
            objects = ["a brave knight", "a magical forest"]

        return self.generate_story(objects)
