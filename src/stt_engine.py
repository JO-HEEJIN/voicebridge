"""Speech-to-Text engine using Deepgram streaming API.

Provides real-time Korean speech transcription with interim and final results.
"""

import asyncio
import sys
from typing import Callable

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
)


class STTEngine:
    """Real-time speech-to-text engine using Deepgram's streaming API."""

    def __init__(self, api_key: str, language: str = "ko"):
        """Initialize the STT engine.

        Args:
            api_key: Deepgram API key.
            language: Language code for transcription (default: "ko" for Korean).
        """
        self._api_key = api_key
        self._language = language
        self._client = None
        self._connection = None
        self._callback = None
        self._reconnect_count = 0
        self._max_reconnects = 3
        self._is_closing = False

    async def connect(self):
        """Establish WebSocket connection to Deepgram."""
        try:
            config = DeepgramClientOptions(options={"keepalive": "true"})
            self._client = DeepgramClient(self._api_key, config)

            self._connection = self._client.listen.asynclive.v("1")

            # Register event handlers
            self._connection.on(LiveTranscriptionEvents.Transcript, self._on_message)
            self._connection.on(LiveTranscriptionEvents.UtteranceEnd, self._on_utterance_end)
            self._connection.on(LiveTranscriptionEvents.Error, self._on_error)
            self._connection.on(LiveTranscriptionEvents.Close, self._on_close)

            # Configure streaming options
            options = LiveOptions(
                language=self._language,
                model="nova-2",
                punctuate=True,
                interim_results=True,
                encoding="linear16",
                sample_rate=16000,
                channels=1,
                utterance_end_ms="1500",
                endpointing=500,
            )

            # Start the connection
            if not await self._connection.start(options):
                raise ConnectionError("Failed to start Deepgram connection")

            self._reconnect_count = 0
            print("STT engine connected", file=sys.stderr)

        except Exception as e:
            print(f"STT connection error: {e}", file=sys.stderr)
            raise

    async def send_audio(self, chunk: bytes):
        """Send audio data to Deepgram for transcription.

        Args:
            chunk: Raw audio bytes (16-bit PCM, 16kHz, mono).
        """
        if self._connection:
            try:
                await self._connection.send(chunk)
            except Exception as e:
                print(f"Error sending audio: {e}", file=sys.stderr)

    def on_transcript(self, callback: Callable[[str, bool], None]):
        """Register callback for transcript results.

        Args:
            callback: Function called with (text, is_final) when transcripts arrive.
        """
        self._callback = callback

    def on_utterance_end(self, callback: Callable[[], None]):
        """Register callback for utterance end events."""
        self._utterance_end_callback = callback

    async def close(self):
        """Close the Deepgram connection."""
        self._is_closing = True
        if self._connection:
            try:
                await self._connection.finish()
                print("STT engine closed", file=sys.stderr)
            except Exception as e:
                print(f"Error closing STT: {e}", file=sys.stderr)

    async def _on_message(self, *args, **kwargs):
        """Handle incoming transcript from Deepgram."""
        try:
            result = args[1] if len(args) > 1 else kwargs.get("result")
            if not result or not result.channel:
                return

            transcript = result.channel.alternatives[0].transcript
            is_final = result.is_final

            # Only process non-empty transcripts
            if transcript and self._callback:
                self._callback(transcript, is_final)

        except Exception as e:
            print(f"Error processing transcript: {e}", file=sys.stderr)

    async def _on_utterance_end(self, *args, **kwargs):
        """Handle utterance end event from Deepgram."""
        if hasattr(self, '_utterance_end_callback') and self._utterance_end_callback:
            self._utterance_end_callback()

    async def _on_error(self, *args, **kwargs):
        """Handle Deepgram errors."""
        error = args[1] if len(args) > 1 else kwargs.get("error")
        print(f"Deepgram error: {error}", file=sys.stderr)

    async def _on_close(self, *args, **kwargs):
        """Handle connection close and attempt reconnection."""
        if self._is_closing:
            return

        print("Deepgram connection closed", file=sys.stderr)

        if self._reconnect_count < self._max_reconnects:
            self._reconnect_count += 1
            print(
                f"Attempting reconnect {self._reconnect_count}/{self._max_reconnects}...",
                file=sys.stderr,
            )
            asyncio.create_task(self._reconnect())
        else:
            print("Max reconnection attempts reached", file=sys.stderr)

    async def _reconnect(self):
        """Attempt to reconnect to Deepgram after a delay."""
        await asyncio.sleep(1)
        try:
            await self.connect()
        except Exception as e:
            print(f"Reconnection failed: {e}", file=sys.stderr)
