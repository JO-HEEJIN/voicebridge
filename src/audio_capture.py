"""Audio capture module for VoiceBridge.

Captures audio from microphone using sounddevice library with callback-based
streaming for low latency.
"""

import asyncio
import queue
from typing import Optional
import sounddevice as sd
import numpy as np


class AudioCapture:
    """Captures audio from microphone and streams it via callbacks.

    Implements FR-01: Audio Capture with configurable sample rate, mono channel,
    and chunk-based streaming for low latency.
    """

    def __init__(
        self,
        device_id: Optional[int] = None,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 4096,
    ):
        """Initialize audio capture.

        Args:
            device_id: Input device ID (None = default device)
            sample_rate: Sample rate in Hz (default 16000 for STT)
            channels: Number of audio channels (default 1 for mono)
            chunk_size: Audio chunk size in frames
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self._stream = None
        self._audio_queue = asyncio.Queue()
        self._callbacks = []

    def _audio_callback(self, indata, frames, time, status):
        """Callback invoked by sounddevice when audio data is available.

        Args:
            indata: Input audio data as numpy array
            frames: Number of frames
            time: Time info
            status: Status flags
        """
        if status:
            print(f"Audio capture status: {status}")

        audio_bytes = indata.copy().tobytes()

        # Put data in asyncio queue for async consumers
        try:
            self._audio_queue.put_nowait(audio_bytes)
        except asyncio.QueueFull:
            pass

        # Call registered callbacks
        for callback in self._callbacks:
            callback(audio_bytes)

    def start(self):
        """Open the audio input stream and start capturing."""
        self._stream = sd.InputStream(
            device=self.device_id,
            channels=self.channels,
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            dtype='int16',
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self):
        """Stop the audio stream and clean up resources."""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    async def get_audio_chunk(self) -> bytes:
        """Get next audio chunk from the queue (async).

        Returns:
            bytes: Raw 16-bit PCM audio data
        """
        return await self._audio_queue.get()

    def on_audio_data(self, callback):
        """Register a callback to receive audio data.

        Args:
            callback: Function to call with audio bytes when data arrives
        """
        self._callbacks.append(callback)
