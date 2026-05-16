"""Application configuration."""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    PROJECT_ROOT: Path = Path(__file__).parent.parent
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    MODELS_CACHE_DIR: Path = PROJECT_ROOT / "models_cache"
    AUDIO_OUTPUT_DIR: Path = PROJECT_ROOT / "audio_output"

    SAMPLE_RATE: int = 16000
    AUDIO_DURATION_SECONDS: int = 15
    CHANNELS: int = 1

    # distil-small.en: ~6x faster than whisper-small at near-equal English WER.
    WHISPER_MODEL: str = "distil-small.en"

    # Story-generation backend: "local" (HuggingFace), "anthropic" (Claude API),
    # or "llama_cpp" (GGUF via llama-cpp-python; CPU-friendly, no CUDA needed).
    STORY_BACKEND: str = "local"

    # Default local model. Phi-3-mini is small, fast on CPU with 4-bit quant, and a
    # solid step up from TinyLlama in narrative coherence.
    TEXT_GENERATION_MODEL: str = "microsoft/Phi-3-mini-4k-instruct"

    # 4-bit quantization via bitsandbytes. Silently falls back to fp32 if unavailable.
    USE_QUANTIZATION: bool = True

    # Anthropic backend config (used when STORY_BACKEND == "anthropic").
    ANTHROPIC_MODEL: str = "claude-haiku-4-5-20251001"
    ANTHROPIC_API_KEY: Optional[str] = None

    # llama-cpp-python (GGUF) backend config. Either set LLAMA_CPP_MODEL_PATH to a
    # local .gguf file, or leave it empty and the model will be pulled from
    # HF Hub using REPO+FILE (cached under ~/.cache/huggingface/).
    LLAMA_CPP_MODEL_PATH: Optional[str] = None
    LLAMA_CPP_MODEL_REPO: str = "microsoft/Phi-3-mini-4k-instruct-gguf"
    LLAMA_CPP_MODEL_FILE: str = "Phi-3-mini-4k-instruct-q4.gguf"
    LLAMA_CPP_N_CTX: int = 4096
    # None lets llama.cpp pick a sensible default (typically all physical cores).
    LLAMA_CPP_N_THREADS: Optional[int] = None

    # TTS chain: "kokoro" -> "piper" -> "pyttsx3". The chosen engine is
    # the first one in the chain starting at TTS_ENGINE that initializes.
    TTS_ENGINE: str = "kokoro"
    KOKORO_VOICE: str = "af_heart"
    KOKORO_LANG: str = "a"  # 'a' = American English, 'b' = British English

    # Interpreted as max_new_tokens for the generate call.
    MAX_STORY_LENGTH: int = 400
    TEMPERATURE: float = 0.8
    TOP_P: float = 0.95

    # Story content controls.
    DEFAULT_AGE_RANGE: str = "5-8"
    DEFAULT_TONE: str = "adventurous"
    STRUCTURED_GENERATION: bool = True
    CONVERSATION_HISTORY_LIMIT: int = 4

    # Critique-revise refinement. 0 = off (default).
    # Each round adds ~2x the inference cost of a single generation.
    STORY_REFINEMENT_ROUNDS: int = 0

    # When True, every LLM call's input messages and output response are
    # printed to stdout. Useful for debugging prompts and refinement loops.
    LOG_LLM_CALLS: bool = False

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "<level>{level: <8}</level> | <cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    ENABLE_API: bool = False
    API_PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def __post_init__(self) -> None:
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()

for _dir in (settings.LOGS_DIR, settings.MODELS_CACHE_DIR, settings.AUDIO_OUTPUT_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
