"""Main Story Teller Bot orchestrator."""
import argparse
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from loguru import logger

from config.settings import settings
from src.audio_handler import AudioInputHandler, AudioOutputHandler
from src.safety import SafetyFilter
from src.speech_recognizer import SpeechRecognizer
from src.story_generator import StoryGenerator


SAFE_FALLBACK_STORY = (
    "Let's try a different idea. Once upon a time, a little fox and a wise owl "
    "set out to find the brightest star in the forest. Along the way, they "
    "shared their snacks with a hungry hedgehog and learned that kindness shines "
    "even brighter than starlight. The end."
)

UNSAFE_INPUT_REPLY = (
    "Let's pick a different story idea. Tell me about animals, magic, space, "
    "or a brave adventure!"
)


class BotState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    PAUSED = "paused"
    STOPPED = "stopped"


class StoryTellerBot:
    """Main Story Teller Bot."""

    def __init__(self):
        self.state = BotState.IDLE
        self.audio_input = AudioInputHandler()
        self.audio_output = AudioOutputHandler()
        self.speech_recognizer = SpeechRecognizer()
        self.story_generator = StoryGenerator()
        self.safety = SafetyFilter(enable_classifier=False)
        self.current_story: Optional[str] = None
        self.current_story_file: Optional[Path] = None
        logger.info("Story Teller Bot initialized.")

    # -- main loop ---------------------------------------------------------

    def start(self) -> None:
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
                    self._continue_story_mode()
                elif choice == "4":
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
        print("\n" + "=" * 50)
        print("STORY TELLER BOT FOR KIDS")
        print("=" * 50)
        print("1. Tell Story (Audio Input)")
        print("2. Tell Story (Text Input)")
        print("3. Continue Last Story")
        print("4. Exit")
        print("=" * 50)

    # -- modes -------------------------------------------------------------

    def _interactive_story_mode(self) -> None:
        try:
            print("\nPlease tell me what story you'd like to hear...")
            print("(Speak about objects or characters you want in the story)")
            print(f"Recording for up to {settings.AUDIO_DURATION_SECONDS} seconds...")

            self.state = BotState.LISTENING
            audio_data = self.audio_input.record_audio()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = settings.AUDIO_OUTPUT_DIR / f"input_{timestamp}.wav"
            self.audio_input.save_audio(audio_file, audio_data)

            print("\nProcessing your request...")
            self.state = BotState.PROCESSING
            user_text = self.speech_recognizer.transcribe_from_file(audio_file)
            print(f"I heard: '{user_text}'")

            if not user_text.strip():
                print("I couldn't hear you clearly. Let's try again.")
                return

            self._generate_and_play(user_text)
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"Error: {e}")

    def _text_input_mode(self) -> None:
        try:
            print("\nTell me what story you'd like (e.g., 'story with a king and a lion'):")
            user_input = input("> ").strip()
            if not user_input:
                print("Please provide input.")
                return
            self._generate_and_play(user_input)
        except Exception as e:
            logger.error(f"Error in text mode: {e}")
            print(f"Error: {e}")

    def _continue_story_mode(self) -> None:
        if not self.current_story:
            print("\nNo story to continue yet. Start a new one first.")
            return
        try:
            print("\nWhat happens next? (Press Enter for 'tell me what happened next')")
            follow_up = input("> ").strip() or "What happens next?"
            input_check = self.safety.check_input(follow_up)
            if not input_check.is_safe:
                logger.warning(f"Unsafe follow-up blocked: {input_check.reason}")
                print(UNSAFE_INPUT_REPLY)
                return

            print("Continuing your story...")
            self.state = BotState.PROCESSING
            continuation = self.story_generator.continue_story(follow_up)
            continuation = self._guard_output(continuation, original_input=follow_up, is_continuation=True)

            self.current_story = continuation
            print(f"\nStory continues:\n{continuation}\n")
            self._play_story()
        except Exception as e:
            logger.error(f"Error continuing story: {e}")
            print(f"Error: {e}")

    # -- shared generate+play with safety ----------------------------------

    def _generate_and_play(self, user_input: str) -> None:
        input_check = self.safety.check_input(user_input)
        if not input_check.is_safe:
            logger.warning(f"Unsafe input blocked: {input_check.reason}")
            print(UNSAFE_INPUT_REPLY)
            return

        print("Generating your story...")
        self.state = BotState.PROCESSING
        raw_story = self.story_generator.generate_story_from_input(user_input)
        story = self._guard_output(raw_story, original_input=user_input)

        self.current_story = story
        print(f"\nStory:\n{story}\n")
        self._play_story()

    def _guard_output(self, story: str, original_input: str, is_continuation: bool = False) -> str:
        """Check the generated story; one retry, then safe fallback."""
        check = self.safety.check_output(story)
        if check.is_safe:
            return story

        logger.warning(f"Unsafe output blocked: {check.reason}; retrying once.")
        if is_continuation:
            retry = self.story_generator.continue_story(original_input)
        else:
            retry = self.story_generator.generate_story_from_input(original_input)

        retry_check = self.safety.check_output(retry)
        if retry_check.is_safe:
            return retry

        logger.error(f"Retry also unsafe ({retry_check.reason}); using fallback story.")
        return SAFE_FALLBACK_STORY

    # -- playback ----------------------------------------------------------

    def _play_story(self) -> None:
        if not self.current_story:
            print("No story to play.")
            return
        try:
            self.state = BotState.SPEAKING
            print("\nPlaying story...")
            print("Controls: (P) Pause, (S) Stop, or let it finish...")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_story_file = settings.AUDIO_OUTPUT_DIR / f"story_{timestamp}.wav"
            self.audio_output.speak(self.current_story, self.current_story_file)

            print("\nStory finished!")
            self.state = BotState.IDLE
        except KeyboardInterrupt:
            logger.info("Story playback interrupted.")
            self.audio_output.stop_playback()
            self.state = BotState.STOPPED
            print("\nStory stopped.")
        except Exception as e:
            logger.error(f"Error playing story: {e}")
            print(f"Error: {e}")

    def generate_story_from_text(self, user_input: str) -> str:
        """Non-interactive entry point (CLI mode)."""
        logger.info(f"Generating story from text input: {user_input}")
        input_check = self.safety.check_input(user_input)
        if not input_check.is_safe:
            logger.warning(f"Unsafe input blocked: {input_check.reason}")
            print(UNSAFE_INPUT_REPLY)
            return ""

        print("Generating your story...")
        self.state = BotState.PROCESSING
        raw_story = self.story_generator.generate_story_from_input(user_input)
        story = self._guard_output(raw_story, original_input=user_input)

        self.current_story = story
        print(f"\nStory:\n{story}\n")

        print("Playing story...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_story_file = settings.AUDIO_OUTPUT_DIR / f"story_{timestamp}.wav"
        self.audio_output.speak(story, self.current_story_file)
        print("\nStory finished!")
        return story

    def _exit_bot(self) -> None:
        print("\nThank you for using Story Teller Bot! Goodbye!")
        logger.info("Story Teller Bot stopped.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Story Teller Bot - Generate stories for kids",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.bot                            # Interactive mode
  python -m src.bot --text "king and a lion"  # Non-interactive
  python -m src.bot --help                     # Show help
        """,
    )
    parser.add_argument("--text", type=str, help="Generate story from text (non-interactive)")
    parser.add_argument("--no-play", action="store_true", help="Generate story but don't play it")
    args = parser.parse_args()

    logger.add(
        settings.LOGS_DIR / "story_teller_bot.log",
        rotation="500 MB",
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
    )

    bot = StoryTellerBot()

    if args.text:
        logger.info(f"Non-interactive mode: generating story from text: {args.text}")
        try:
            if args.no_play:
                bot.state = BotState.PROCESSING
                input_check = bot.safety.check_input(args.text)
                if not input_check.is_safe:
                    print(UNSAFE_INPUT_REPLY)
                    return
                raw_story = bot.story_generator.generate_story_from_input(args.text)
                story = bot._guard_output(raw_story, original_input=args.text)
                print(f"\nStory:\n{story}\n")
                logger.info("Story generated (not played).")
            else:
                bot.generate_story_from_text(args.text)
                logger.info("Story generated and played.")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")
            exit(1)
    else:
        bot.start()


if __name__ == "__main__":
    main()
