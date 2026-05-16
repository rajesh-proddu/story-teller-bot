"""
Audio input/output handler for Story Teller Bot.
Handles recording audio from microphone and text-to-speech playback.

Output uses Piper TTS (neural, natural-sounding) by default with a
pyttsx3 fallback if Piper is unavailable or the voice model is missing.
"""
import io
import re
import threading
import wave
from pathlib import Path
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass

import sounddevice as sd
import soundfile as sf
import numpy as np
from loguru import logger

from config.settings import settings


# Piper voice model defaults. Voice models are .onnx files placed in
# settings.MODELS_CACHE_DIR. Each model also requires a sibling .onnx.json
# config file in the same directory.
DEFAULT_PIPER_VOICE = "en_US-amy-medium"
ALTERNATE_PIPER_VOICE = "en_US-ryan-medium"
PIPER_VOICE_DOWNLOAD_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "en/en_US/amy/medium/en_US-amy-medium.onnx"
)
PIPER_VOICE_CONFIG_DOWNLOAD_URL = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
    "en/en_US/amy/medium/en_US-amy-medium.onnx.json"
)

# Kokoro TTS (Hexgrad). 82M neural model; ~24 kHz output; requires espeak-ng
# at the system level for English phonemization.
KOKORO_SAMPLE_RATE = 24000


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
    """Handles audio output and text-to-speech.

    Default engine is Piper TTS (neural). Falls back to pyttsx3 if Piper
    or its voice model is unavailable.
    """

    def __init__(self, engine: Optional[str] = None):
        """Initialize audio output handler.

        Args:
            engine: TTS engine name ("piper" or "pyttsx3"). Defaults to
                settings.TTS_ENGINE.
        """
        requested = (engine or getattr(settings, "TTS_ENGINE", "kokoro")).lower()
        self.is_playing = False
        self.playback_thread: Optional[threading.Thread] = None

        # Kokoro state.
        self._kokoro_pipeline = None  # type: ignore[var-annotated]
        self._kokoro_voice: str = getattr(settings, "KOKORO_VOICE", "af_heart")

        # Piper state (populated only when the Piper engine is active).
        self._piper_voice = None  # type: ignore[var-annotated]
        self._piper_alt_voice = None  # type: ignore[var-annotated]
        self._piper_sample_rate: int = 22050

        # pyttsx3 state (used either as primary or fallback).
        self._pyttsx3_engine = None  # type: ignore[var-annotated]

        self.engine_name = self._init_engine(requested)
        logger.info(f"AudioOutputHandler initialized with TTS engine: {self.engine_name}")

    # ------------------------------------------------------------------
    # Engine setup
    # ------------------------------------------------------------------
    def _init_engine(self, requested: str) -> str:
        """Initialize TTS engine with chain fallback: kokoro -> piper -> pyttsx3."""
        chain = ["kokoro", "piper", "pyttsx3"]
        if requested in chain:
            chain = chain[chain.index(requested):]

        for name in chain:
            if name == "kokoro" and self._init_kokoro():
                return "kokoro"
            if name == "piper" and self._init_piper():
                return "piper"
            if name == "pyttsx3":
                self._init_pyttsx3()
                return "pyttsx3"
            logger.warning(f"TTS engine '{name}' unavailable; trying next in chain.")

        self._init_pyttsx3()
        return "pyttsx3"

    def _init_kokoro(self) -> bool:
        """Try to load Kokoro neural TTS pipeline."""
        try:
            from kokoro import KPipeline  # type: ignore
        except ImportError:
            logger.warning(
                "kokoro package not installed; cannot use Kokoro TTS. "
                "Install with: pip install kokoro (also requires system 'espeak-ng')."
            )
            return False

        try:
            lang_code = getattr(settings, "KOKORO_LANG", "a")
            self._kokoro_pipeline = KPipeline(lang_code=lang_code)
            logger.info(
                f"Loaded Kokoro pipeline (lang={lang_code}, voice={self._kokoro_voice})"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Kokoro pipeline: {e}")
            self._kokoro_pipeline = None
            return False

    def _init_piper(self) -> bool:
        """Try to load Piper and the default voice model.

        Returns:
            True if Piper is ready to synthesize, False otherwise.
        """
        try:
            from piper import PiperVoice  # type: ignore
        except ImportError:
            logger.warning(
                "piper-tts package is not installed; cannot use Piper TTS. "
                "Install with: pip install piper-tts"
            )
            return False

        model_path = self._piper_model_path(DEFAULT_PIPER_VOICE)
        if not model_path.exists():
            logger.error(
                "Piper voice model not found at {}. Download it from {} "
                "(and the matching .onnx.json from {}) and place both files "
                "in {}.",
                model_path,
                PIPER_VOICE_DOWNLOAD_URL,
                PIPER_VOICE_CONFIG_DOWNLOAD_URL,
                settings.MODELS_CACHE_DIR,
            )
            return False

        try:
            self._piper_voice = PiperVoice.load(str(model_path))
            self._piper_sample_rate = self._detect_piper_sample_rate(self._piper_voice)
            logger.info(
                f"Loaded Piper voice '{DEFAULT_PIPER_VOICE}' "
                f"(sample_rate={self._piper_sample_rate} Hz)"
            )
        except Exception as e:
            logger.error(f"Failed to load Piper voice model: {e}")
            self._piper_voice = None
            return False

        # Optional alternate voice for multi-character narration.
        alt_path = self._piper_model_path(ALTERNATE_PIPER_VOICE)
        if alt_path.exists():
            try:
                self._piper_alt_voice = PiperVoice.load(str(alt_path))
                logger.info(f"Loaded alternate Piper voice '{ALTERNATE_PIPER_VOICE}'")
            except Exception as e:
                logger.warning(f"Could not load alternate Piper voice: {e}")
                self._piper_alt_voice = None
        else:
            logger.debug(
                f"Alternate Piper voice '{ALTERNATE_PIPER_VOICE}' not found; "
                "multi-character output will use the default voice only."
            )

        return True

    def _init_pyttsx3(self) -> None:
        """Initialize the pyttsx3 engine (primary or fallback)."""
        try:
            import pyttsx3  # type: ignore

            self._pyttsx3_engine = pyttsx3.init()
            self._pyttsx3_engine.setProperty("rate", 150)
            self._pyttsx3_engine.setProperty("volume", 0.9)
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 engine: {e}")
            self._pyttsx3_engine = None

    @staticmethod
    def _piper_model_path(voice_name: str) -> Path:
        """Return the expected on-disk path for a Piper voice model."""
        return Path(settings.MODELS_CACHE_DIR) / f"{voice_name}.onnx"

    @staticmethod
    def _detect_piper_sample_rate(voice) -> int:
        """Best-effort lookup of the voice's native sample rate."""
        try:
            cfg = getattr(voice, "config", None)
            if cfg is not None:
                sr = getattr(cfg, "sample_rate", None)
                if isinstance(sr, int) and sr > 0:
                    return sr
        except Exception:
            pass
        return 22050

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def speak(self, text: str, save_to_file: Optional[Path] = None) -> None:
        """Convert text to speech and play it.

        Args:
            text: Text to speak.
            save_to_file: Optional path to write a WAV file of the speech.
        """
        if not text:
            logger.warning("speak() called with empty text; nothing to do.")
            return

        logger.info(f"Speaking text ({self.engine_name}): {text[:100]}...")
        try:
            if self.engine_name == "kokoro" and self._kokoro_pipeline is not None:
                self._speak_kokoro(text, save_to_file)
            elif self.engine_name == "piper" and self._piper_voice is not None:
                self._speak_piper(text, self._piper_voice, save_to_file)
            else:
                self._speak_pyttsx3(text, save_to_file)
        except Exception as e:
            logger.error(f"Error during text-to-speech: {e}")
            raise

    def speak_with_voices(self, text: str, save_to_file: Optional[Path] = None) -> None:
        """Speak text with two voices: narration vs. quoted dialogue.

        Quoted segments (text in double quotes) use an alternate voice if
        available; otherwise the default voice is used for everything.
        Falls back to plain ``speak`` when Piper is not the active engine.

        Args:
            text: Story text. Double-quoted spans are treated as dialogue.
            save_to_file: Optional path to write a combined WAV file.
        """
        if not text:
            logger.warning("speak_with_voices() called with empty text; nothing to do.")
            return

        if self.engine_name != "piper" or self._piper_voice is None:
            logger.info("Multi-voice playback requires Piper; using default speak().")
            self.speak(text, save_to_file=save_to_file)
            return

        alt = self._piper_alt_voice or self._piper_voice
        if self._piper_alt_voice is None:
            logger.info(
                "Alternate Piper voice not loaded; dialogue will use the default voice."
            )

        segments = self._split_narration_and_dialogue(text)
        chunks: List[np.ndarray] = []

        self.is_playing = True
        try:
            for kind, segment in segments:
                if not segment.strip():
                    continue
                voice = alt if kind == "dialogue" else self._piper_voice
                audio = self._synthesize_piper(segment, voice)
                if audio.size == 0:
                    continue
                chunks.append(audio)
                if self.is_playing:
                    sd.play(audio, self._piper_sample_rate)
                    sd.wait()
        finally:
            self.is_playing = False

        if save_to_file and chunks:
            combined = np.concatenate(chunks)
            self._write_wav(save_to_file, combined, self._piper_sample_rate)
            logger.info(f"Audio saved to {save_to_file}")

    def play_audio(self, audio_file: Path) -> None:
        """Play an audio file from disk.

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
            self.is_playing = False
            logger.error(f"Error playing audio: {e}")
            raise

    def pause_playback(self) -> None:
        """Pause (stop) current playback. Resume is not supported."""
        if self.is_playing:
            sd.stop()
            logger.info("Playback paused.")

    def resume_playback(self) -> None:
        """Resume playback (not supported)."""
        logger.warning("Resume not supported; please replay from beginning.")

    def stop_playback(self) -> None:
        """Stop any in-progress playback."""
        if self.is_playing:
            sd.stop()
            self.is_playing = False
            logger.info("Playback stopped.")
        if self._pyttsx3_engine is not None:
            try:
                self._pyttsx3_engine.stop()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _speak_piper(
        self,
        text: str,
        voice,
        save_to_file: Optional[Path],
    ) -> None:
        """Synthesize with Piper and play; optionally save to WAV."""
        audio = self._synthesize_piper(text, voice)
        if audio.size == 0:
            logger.warning("Piper produced no audio for the given text.")
            return

        if save_to_file:
            self._write_wav(save_to_file, audio, self._piper_sample_rate)
            logger.info(f"Audio saved to {save_to_file}")

        self.is_playing = True
        try:
            sd.play(audio, self._piper_sample_rate)
            sd.wait()
        finally:
            self.is_playing = False

    def _synthesize_piper(self, text: str, voice) -> np.ndarray:
        """Run Piper synthesis and return a float32 mono numpy array.

        Handles the two common Piper API shapes:
        - ``synthesize(text)`` returning an iterable of audio chunks
          (objects with ``audio_int16_bytes`` / ``audio_int16_array`` /
          ``audio_float_array`` attributes, or raw bytes / ndarrays).
        - ``synthesize_wav(text, wav_file)`` writing a WAV stream.
        """
        # Preferred path: iterate over chunks from synthesize().
        if hasattr(voice, "synthesize"):
            try:
                pieces: List[np.ndarray] = []
                for chunk in voice.synthesize(text):
                    arr = self._coerce_piper_chunk(chunk)
                    if arr is not None and arr.size > 0:
                        pieces.append(arr)
                if pieces:
                    return np.concatenate(pieces).astype(np.float32, copy=False)
            except TypeError:
                # Older API: synthesize wrote to a wave_file kwarg.
                pass
            except Exception as e:
                logger.debug(f"Piper synthesize() iteration failed: {e}")

        # Fallback path: synthesize to an in-memory WAV.
        buf = io.BytesIO()
        try:
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self._piper_sample_rate)
                if hasattr(voice, "synthesize_wav"):
                    voice.synthesize_wav(text, wf)
                else:
                    voice.synthesize(text, wf)  # type: ignore[misc]
        except Exception as e:
            logger.error(f"Piper WAV synthesis failed: {e}")
            return np.zeros(0, dtype=np.float32)

        buf.seek(0)
        try:
            data, _ = sf.read(buf, dtype="float32")
            return np.asarray(data, dtype=np.float32)
        except Exception as e:
            logger.error(f"Could not decode Piper WAV output: {e}")
            return np.zeros(0, dtype=np.float32)

    @staticmethod
    def _coerce_piper_chunk(chunk) -> Optional[np.ndarray]:
        """Normalize a Piper chunk into a float32 mono numpy array."""
        if chunk is None:
            return None

        # Common attribute shapes on AudioChunk-like objects.
        for attr in ("audio_float_array", "audio_float32"):
            arr = getattr(chunk, attr, None)
            if arr is not None:
                return np.asarray(arr, dtype=np.float32)

        arr = getattr(chunk, "audio_int16_array", None)
        if arr is not None:
            return np.asarray(arr, dtype=np.int16).astype(np.float32) / 32768.0

        raw = getattr(chunk, "audio_int16_bytes", None)
        if raw is not None:
            return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

        if isinstance(chunk, (bytes, bytearray)):
            return np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0

        if isinstance(chunk, np.ndarray):
            if chunk.dtype == np.int16:
                return chunk.astype(np.float32) / 32768.0
            return chunk.astype(np.float32, copy=False)

        return None

    def _write_wav(self, path: Path, audio: np.ndarray, sample_rate: int) -> None:
        """Write a float32 mono numpy array to a 16-bit PCM WAV file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(path), audio, sample_rate, subtype="PCM_16")

    def _speak_kokoro(self, text: str, save_to_file: Optional[Path]) -> None:
        """Synthesize with Kokoro and play; optionally save to WAV."""
        audio = self._synthesize_kokoro(text)
        if audio.size == 0:
            logger.warning("Kokoro produced no audio for the given text.")
            return

        if save_to_file:
            self._write_wav(save_to_file, audio, KOKORO_SAMPLE_RATE)
            logger.info(f"Audio saved to {save_to_file}")

        self.is_playing = True
        try:
            sd.play(audio, KOKORO_SAMPLE_RATE)
            sd.wait()
        finally:
            self.is_playing = False

    def _synthesize_kokoro(self, text: str) -> np.ndarray:
        """Run Kokoro synthesis and return a float32 mono numpy array at 24 kHz."""
        try:
            generator = self._kokoro_pipeline(text, voice=self._kokoro_voice)
            pieces: List[np.ndarray] = []
            for result in generator:
                # Kokoro yields (graphemes, phonemes, audio) tuples.
                audio = result[-1] if isinstance(result, tuple) else result
                if hasattr(audio, "detach"):
                    audio = audio.detach().cpu().numpy()
                arr = np.asarray(audio, dtype=np.float32)
                if arr.ndim > 1:
                    arr = arr.reshape(-1)
                if arr.size > 0:
                    pieces.append(arr)
            if not pieces:
                return np.zeros(0, dtype=np.float32)
            return np.concatenate(pieces).astype(np.float32, copy=False)
        except Exception as e:
            logger.error(f"Kokoro synthesis failed: {e}")
            return np.zeros(0, dtype=np.float32)

    def _speak_pyttsx3(self, text: str, save_to_file: Optional[Path]) -> None:
        """Speak using pyttsx3 (legacy / fallback engine)."""
        if self._pyttsx3_engine is None:
            raise RuntimeError("pyttsx3 engine is not available.")

        if save_to_file:
            self._pyttsx3_engine.save_to_file(text, str(save_to_file))
            logger.info(f"Audio saved to {save_to_file}")

        self.is_playing = True
        try:
            self._pyttsx3_engine.say(text)
            self._pyttsx3_engine.runAndWait()
        finally:
            self.is_playing = False

    @staticmethod
    def _split_narration_and_dialogue(text: str) -> List[Tuple[str, str]]:
        """Split text into ('narration' | 'dialogue', segment) tuples.

        Anything inside straight or curly double quotes counts as dialogue;
        everything else is narration. Order is preserved.
        """
        pattern = re.compile(r"[\"“]([^\"“”]+)[\"”]")
        segments: List[Tuple[str, str]] = []
        idx = 0
        for match in pattern.finditer(text):
            if match.start() > idx:
                segments.append(("narration", text[idx:match.start()]))
            segments.append(("dialogue", match.group(1)))
            idx = match.end()
        if idx < len(text):
            segments.append(("narration", text[idx:]))
        return segments
