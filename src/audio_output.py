"""Audio output module for VoiceBridge.

Plays TTS audio through configured output device (targeting BlackHole).
"""

import asyncio
from typing import Optional
import sounddevice as sd
import numpy as np


class AudioOutput:
    """Plays audio through output device with async support.

    Implements FR-06: Audio Output with sequential playback (no overlap)
    and configurable output device selection.
    """

    def __init__(
        self,
        device_id: Optional[int] = None,
        sample_rate: int = 24000,
    ):
        """Initialize audio output.

        Args:
            device_id: Output device ID (None = default device)
            sample_rate: Sample rate in Hz (default 24000 for TTS)
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self._playback_lock = asyncio.Lock()

    def start(self):
        """Ready the output (no-op for sounddevice.play approach)."""
        pass

    def stop(self):
        """Clean up resources."""
        sd.stop()

    async def play(self, audio_data: bytes):
        """Play PCM audio bytes through the output device.

        Uses asyncio.Lock to prevent overlapping playback per FR-06.2.

        Args:
            audio_data: Raw 16-bit PCM audio bytes
        """
        async with self._playback_lock:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Normalize to float32 range [-1.0, 1.0] for playback
            audio_float = audio_array.astype(np.float32) / 32768.0

            # Create a future to wait for playback completion
            event = asyncio.Event()

            def callback():
                """Called when playback finishes."""
                event.set()

            # Play audio (blocking call in sync context)
            sd.play(
                audio_float,
                samplerate=self.sample_rate,
                device=self.device_id,
                blocking=False,
            )

            # Wait for playback to complete
            sd.wait()
