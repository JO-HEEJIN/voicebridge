"""Text-to-Speech engine using KittenTTS (local, no API needed).

Super-tiny expressive TTS model running entirely on CPU.
"""

import sys
import numpy as np
from kittentts import KittenTTS


class TTSEngine:
    """Synthesizes speech from text using KittenTTS locally."""

    VOICES = ["Bella", "Jasper", "Luna", "Bruno", "Rosie", "Hugo", "Kiki", "Leo"]

    def __init__(self, voice: str = "Bella", model: str = "KittenML/kitten-tts-mini-0.8"):
        """Initialize TTS engine.

        Args:
            voice: Voice name (Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo)
            model: HuggingFace model ID
        """
        self._voice = voice
        self._model_id = model
        self._model = None
        self._sample_rate = 24000

    def load(self):
        """Load KittenTTS model (one-time, downloads on first run)."""
        print(f"[SYSTEM] Loading KittenTTS ({self._model_id})...", file=sys.stderr)
        self._model = KittenTTS(self._model_id)
        print(f"[SYSTEM] KittenTTS loaded. Voice: {self._voice}", file=sys.stderr)

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text.

        Args:
            text: Text to convert to speech

        Returns:
            PCM audio bytes (16-bit, 24000Hz, mono), or empty bytes on error
        """
        if not text or not text.strip() or not self._model:
            return b""

        try:
            audio_float = self._model.generate(text, voice=self._voice)
            audio_int16 = (audio_float * 32767).astype(np.int16)
            return audio_int16.tobytes()

        except Exception as e:
            print(f"TTS error: {e}", file=sys.stderr)
            return b""

    def set_voice(self, voice: str):
        """Set the TTS voice."""
        self._voice = voice

    @property
    def sample_rate(self) -> int:
        return self._sample_rate
