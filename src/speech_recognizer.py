"""Offline speech recognition using faster-whisper with optional Silero VAD pre-check."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

import numpy as np
from loguru import logger

from config.settings import settings

AudioInput = Union[Path, np.ndarray, str]


class SpeechRecognizer:
    """Offline speech recognition backed by faster-whisper."""

    def __init__(self, model_name: str = settings.WHISPER_MODEL) -> None:
        self.model_name: str = model_name
        self._model: Optional[Any] = None
        self._vad_model: Optional[Any] = None
        self._vad_unavailable: bool = False
        logger.info(f"SpeechRecognizer configured with faster-whisper model '{model_name}' (lazy load).")

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as e:
            logger.error(f"faster-whisper is not installed: {e}")
            raise
        logger.info(f"Loading faster-whisper '{self.model_name}' (device=cpu, compute_type=int8)...")
        self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        logger.info("faster-whisper model loaded.")
        return self._model

    def _load_vad(self) -> Optional[Any]:
        if self._vad_model is not None:
            return self._vad_model
        if self._vad_unavailable:
            return None
        try:
            import torch  # type: ignore

            logger.info("Loading Silero VAD via torch.hub...")
            model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                trust_repo=True,
            )
            self._vad_model = (model, utils, torch)
            logger.info("Silero VAD loaded.")
            return self._vad_model
        except Exception as e:
            logger.warning(f"Silero VAD unavailable, skipping VAD pre-check: {e}")
            self._vad_unavailable = True
            return None

    def _has_speech(self, audio: np.ndarray, sample_rate: int) -> bool:
        vad = self._load_vad()
        if vad is None:
            return True
        try:
            model, utils, torch = vad
            get_speech_timestamps = utils[0]
            tensor = torch.from_numpy(audio.astype(np.float32))
            timestamps = get_speech_timestamps(tensor, model, sampling_rate=sample_rate)
            return bool(timestamps)
        except Exception as e:
            logger.warning(f"VAD inference failed, assuming speech present: {e}")
            return True

    @staticmethod
    def _prepare_array(audio: np.ndarray) -> np.ndarray:
        arr = audio
        if arr.ndim > 1:
            logger.info(f"Multichannel audio (shape={arr.shape}); averaging to mono.")
            arr = arr.mean(axis=-1) if arr.shape[-1] <= 8 else arr.mean(axis=0)
        if arr.dtype != np.float32:
            if np.issubdtype(arr.dtype, np.integer):
                max_val = float(np.iinfo(arr.dtype).max)
                arr = arr.astype(np.float32) / max_val
            else:
                arr = arr.astype(np.float32)
        return arr

    def transcribe(self, audio_input: AudioInput, language: str = "en") -> str:
        """Transcribe audio from a path or numpy array."""
        model = self._load_model()
        try:
            if isinstance(audio_input, (Path, str)):
                path = Path(audio_input)
                if not path.exists():
                    raise FileNotFoundError(f"Audio file not found: {path}")
                logger.info(f"Transcribing file '{path}' (lang={language}, vad_filter=True)...")
                segments, _info = model.transcribe(str(path), language=language, vad_filter=True)
            elif isinstance(audio_input, np.ndarray):
                arr = self._prepare_array(audio_input)
                sample_rate = settings.SAMPLE_RATE
                if sample_rate != 16000:
                    logger.warning(
                        f"SAMPLE_RATE={sample_rate} != 16000; faster-whisper expects 16kHz."
                    )
                if not self._has_speech(arr, sample_rate):
                    logger.warning("No speech detected; returning empty transcript.")
                    return ""
                logger.info(f"Transcribing numpy array (samples={arr.shape[0]}, lang={language})...")
                segments, _info = model.transcribe(arr, language=language)
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_input)}")

            text = "".join(segment.text for segment in segments).strip()
            logger.info(f"Transcription complete ({len(text)} chars).")
            return text
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise

    def transcribe_from_file(self, audio_file: Path) -> str:
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        return self.transcribe(audio_file)
