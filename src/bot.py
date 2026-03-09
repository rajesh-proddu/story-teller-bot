"""
Main Story Teller Bot orchestrator.
Coordinates audio input, speech recognition, story generation, and audio output.
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from enum import Enum

from loguru import logger

from config.settings import settings
from src.audio_handler import AudioInputHandler, AudioOutputHandler
from src.speech_recognizer import SpeechRecognizer
from src.story_generator import StoryGenerator


class BotState(Enum):
    """Bot state enumeration."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    PAUSED = "paused"
    STOPPED = "stopped"


class StoryTellerBot:
    """Main Story Teller Bot class."""
    
    def __init__(self):
        """Initialize the Story Teller Bot."""
        self.state = BotState.IDLE
        self.audio_input = AudioInputHandler()
        self.audio_output = AudioOutputHandler()
        self.speech_recognizer = SpeechRecognizer()
        self.story_generator = StoryGenerator()
        self.current_story: Optional[str] = None
        self.current_story_file: Optional[Path] = None
        
        logger.info("Story Teller Bot initialized successfully.")
    
    def start(self) -> None:
        """Start the bot and enter interactive mode."""
        logger.info("Starting Story Teller Bot...")
        
        try:
            while True:
                self._display_menu()
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == "1":
                    self._interactive_story_mode()
                elif choice == "2":
                    self._text_input_mode()
                elif choice == "3":
                    self._exit_bot()
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user.")
            self._exit_bot()
        except Exception as e:
            logger.error(f"Unexpected error in bot: {e}")
            self._exit_bot()
    
    def _display_menu(self) -> None:
        """Display main menu."""
        print("\n" + "="*50)
        print("🎭 STORY TELLER BOT FOR KIDS 🎭")
        print("="*50)
        print("1. Tell Story (Audio Input)")
        print("2. Tell Story (Text Input)")
        print("3. Exit")
        print("="*50)
    
    def _interactive_story_mode(self) -> None:
        """Interactive mode with audio input."""
        try:
            print("\n🎤 Please tell me what story you'd like to hear...")
            print("(Speak clearly about objects or characters you want in the story)")
            print("Recording will start now. Speak for up to 30 seconds...")
            
            self.state = BotState.LISTENING
            
            # Record audio
            audio_data = self.audio_input.record_audio()
            
            # Save recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = settings.AUDIO_OUTPUT_DIR / f"input_{timestamp}.wav"
            self.audio_input.save_audio(audio_file, audio_data)
            
            # Transcribe
            print("\n🎧 Processing your request...")
            self.state = BotState.PROCESSING
            user_text = self.speech_recognizer.transcribe_from_file(audio_file)
            print(f"I heard: '{user_text}'")
            
            # Generate story
            print("✨ Generating your story...")
            self.current_story = self.story_generator.generate_story_from_input(user_text)
            print(f"\n📖 Story:\n{self.current_story}\n")
            
            # Play story
            self._play_story()
            
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"❌ Error: {e}")
    
    def _text_input_mode(self) -> None:
        """Mode with text input."""
        try:
            print("\n📝 Tell me what story you'd like (e.g., 'story with a king and a lion'):")
            user_input = input("> ").strip()
            
            if not user_input:
                print("❌ Please provide input.")
                return
            
            # Generate story
            print("✨ Generating your story...")
            self.state = BotState.PROCESSING
            self.current_story = self.story_generator.generate_story_from_input(user_input)
            print(f"\n📖 Story:\n{self.current_story}\n")
            
            # Play story
            self._play_story()
            
        except Exception as e:
            logger.error(f"Error in text mode: {e}")
            print(f"❌ Error: {e}")
    
    def _play_story(self) -> None:
        """Play the generated story with controls."""
        if not self.current_story:
            print("❌ No story to play.")
            return
        
        try:
            self.state = BotState.SPEAKING
            
            print("\n🔊 Playing story...")
            print("Controls: (P) Pause, (S) Stop, or let it finish...")
            
            # Save story to audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_story_file = settings.AUDIO_OUTPUT_DIR / f"story_{timestamp}.wav"
            
            # Speak the story (pyttsx3 has limited control, but we attempt pause/stop)
            self.audio_output.speak(self.current_story, self.current_story_file)
            
            print("\n✅ Story finished!")
            self.state = BotState.IDLE
            
        except KeyboardInterrupt:
            logger.info("Story playback interrupted.")
            self.audio_output.stop_playback()
            self.state = BotState.STOPPED
            print("\n⏹️  Story stopped.")
        except Exception as e:
            logger.error(f"Error playing story: {e}")
            print(f"❌ Error: {e}")
    
    def _exit_bot(self) -> None:
        """Exit the bot gracefully."""
        print("\n👋 Thank you for using Story Teller Bot! Goodbye!")
        logger.info("Story Teller Bot stopped.")


def main() -> None:
    """Main entry point."""
    logger.add(
        settings.LOGS_DIR / "story_teller_bot.log",
        rotation="500 MB",
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT
    )
    
    bot = StoryTellerBot()
    bot.start()


if __name__ == "__main__":
    main()
