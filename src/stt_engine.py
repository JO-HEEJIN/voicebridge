"""Speech-to-Text engine using faster-whisper (local).

Provides high-accuracy Korean speech transcription using OpenAI Whisper
running locally via CTranslate2. Designed for push-to-talk batch mode.
"""

import sys
import numpy as np
from faster_whisper import WhisperModel


class STTEngine:
    """Local speech-to-text engine using faster-whisper."""

    def __init__(self, model_size: str = "medium"):
        """Initialize the STT engine.

        Args:
            model_size: Whisper model size. Options:
                "tiny", "base", "small", "medium", "large-v3"
                Bigger = more accurate but slower.
        """
        self._model = None
        self._model_size = model_size

    def load(self):
        """Load the Whisper model (one-time, may download on first run)."""
        print(f"[SYSTEM] Loading Whisper {self._model_size} model...", file=sys.stderr)
        self._model = WhisperModel(
            self._model_size,
            device="cpu",
            compute_type="int8",
        )
        print("[SYSTEM] Whisper model loaded.", file=sys.stderr)

    def transcribe(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        """Transcribe audio bytes to Korean text.

        Args:
            audio_bytes: Raw 16-bit PCM audio bytes.
            sample_rate: Audio sample rate in Hz.

        Returns:
            Transcribed Korean text, or empty string if nothing detected.
        """
        if not self._model:
            return ""

        # Convert bytes to float32 numpy array
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        segments, info = self._model.transcribe(
            audio_np,
            language="ko",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()
