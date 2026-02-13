"""Text-to-Speech engine using Edge TTS.

Converts text to speech audio in PCM format for playback.
"""

import io
import subprocess
import sys
import edge_tts


class TTSEngine:
    """Synthesizes speech from text using Edge TTS."""

    def __init__(self, voice: str = "en-US-GuyNeural"):
        """Initialize TTS engine with voice.

        Args:
            voice: Voice ID for Edge TTS (e.g., "en-US-GuyNeural", "de-DE-ConradNeural")
        """
        self._voice = voice
        self._rate = "+15%"  # Slightly faster for real-time feel

    async def synthesize(self, text: str) -> bytes:
        """Synthesize speech from text.

        Args:
            text: Text to convert to speech

        Returns:
            PCM audio bytes (16-bit, 24000Hz, mono), or empty bytes on error
        """
        if not text or not text.strip():
            return b""

        try:
            # Generate speech using Edge TTS (produces MP3)
            communicate = edge_tts.Communicate(text, self._voice, rate=self._rate)

            # Collect MP3 audio bytes
            mp3_data = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    mp3_data.write(chunk["data"])

            mp3_bytes = mp3_data.getvalue()

            if not mp3_bytes:
                print("TTS warning: No audio generated", file=sys.stderr)
                return b""

            # Convert MP3 to PCM using ffmpeg
            pcm_bytes = self._mp3_to_pcm(mp3_bytes)
            return pcm_bytes

        except Exception as e:
            print(f"TTS error: {e}", file=sys.stderr)
            return b""

    def _mp3_to_pcm(self, mp3_data: bytes) -> bytes:
        """Convert MP3 audio to raw PCM format.

        Args:
            mp3_data: MP3 audio bytes

        Returns:
            PCM audio bytes (16-bit, 24000Hz, mono)
        """
        try:
            # Use ffmpeg to convert MP3 to PCM
            # -f s16le: signed 16-bit little-endian PCM
            # -ar 24000: sample rate 24000Hz
            # -ac 1: mono (1 channel)
            process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i", "pipe:0",  # Read from stdin
                    "-f", "s16le",   # Output format: signed 16-bit PCM
                    "-ar", "24000",  # Sample rate: 24000Hz
                    "-ac", "1",      # Channels: mono
                    "pipe:1",        # Write to stdout
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            pcm_data, stderr = process.communicate(input=mp3_data)

            if process.returncode != 0:
                print(f"ffmpeg conversion failed: {stderr.decode()}", file=sys.stderr)
                print("TTS warning: Returning MP3 audio (ffmpeg unavailable)", file=sys.stderr)
                return mp3_data

            return pcm_data

        except FileNotFoundError:
            print("TTS warning: ffmpeg not found, returning MP3 audio", file=sys.stderr)
            return mp3_data
        except Exception as e:
            print(f"TTS conversion error: {e}", file=sys.stderr)
            return mp3_data

    def set_voice(self, voice_id: str):
        """Set the TTS voice.

        Args:
            voice_id: Voice ID for Edge TTS (e.g., "en-US-GuyNeural", "de-DE-ConradNeural")
        """
        self._voice = voice_id
