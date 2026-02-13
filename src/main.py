#!/usr/bin/env python3
"""Main controller for VoiceBridge - Real-Time Voice Translation Tool.

Orchestrates the full pipeline from microphone input to translated audio output.
"""

import argparse
import asyncio
import sys
import time
from datetime import datetime

from config import Config
from audio_capture import AudioCapture
from audio_output import AudioOutput
from stt_engine import STTEngine
from sentence_buffer import SentenceBuffer
from translator import Translator
from tts_engine import TTSEngine


class Controller:
    """Main controller orchestrating the VoiceBridge pipeline."""

    def __init__(
        self,
        config: Config,
        input_device: int | None,
        output_device: int | None,
    ):
        """Initialize controller with configuration.

        Args:
            config: Application configuration
            input_device: Input device ID (None = default)
            output_device: Output device ID (None = default)
        """
        self.config = config
        self.target_language = config.target_language
        self.is_running = False

        # Initialize modules
        self.audio_capture = AudioCapture(
            device_id=input_device,
            sample_rate=config.sample_rate,
        )
        self.audio_output = AudioOutput(device_id=output_device)
        self.stt = STTEngine(config.deepgram_api_key)
        self.buffer = SentenceBuffer()
        self.translator = Translator(
            config.anthropic_api_key,
            target_language=self.target_language,
        )
        self.tts = TTSEngine(voice=self._get_voice_for_language(self.target_language))

    def _get_voice_for_language(self, lang: str) -> str:
        """Get TTS voice ID for target language.

        Args:
            lang: Language code ("en" or "de")

        Returns:
            Voice ID string for Edge TTS
        """
        return "en-US-GuyNeural" if lang == "en" else "de-DE-ConradNeural"

    def _display_header(self):
        """Display terminal header with current state."""
        lang_name = "English" if self.target_language == "en" else "German"
        status = "Listening" if self.is_running else "Stopped"
        print("\n" + "=" * 60)
        print(f"VoiceBridge v1.0 | Target: {lang_name} | Status: {status}")
        print("=" * 60)
        print("Commands: [q]uit | [l]anguage toggle | [c]lear buffer")
        print("=" * 60 + "\n")

    def toggle_language(self):
        """Toggle between English and German target languages."""
        self.target_language = "de" if self.target_language == "en" else "en"
        self.translator.set_target_language(self.target_language)
        self.tts.set_voice(self._get_voice_for_language(self.target_language))
        lang_name = "English" if self.target_language == "en" else "German"
        print(f"\n[SYSTEM] Language toggled to {lang_name}\n")

    async def start(self):
        """Start the VoiceBridge pipeline."""
        self.is_running = True
        self._display_header()

        # Start audio modules
        self.audio_capture.start()
        self.audio_output.start()

        # Connect STT engine
        print("[SYSTEM] Connecting to Deepgram...", file=sys.stderr)
        await self.stt.connect()

        # Register STT callback to feed sentence buffer
        def on_transcript(text: str, is_final: bool):
            if is_final:
                self.buffer.add_final(text)
            else:
                self.buffer.add_partial(text)

        self.stt.on_transcript(on_transcript)

        # Register audio callback to send to STT
        self.audio_capture.on_audio_data(
            lambda chunk: asyncio.create_task(self.stt.send_audio(chunk))
        )

        print("[SYSTEM] Pipeline started. Start speaking in Korean...\n")

    async def stop(self):
        """Stop the VoiceBridge pipeline and clean up."""
        self.is_running = False
        print("\n[SYSTEM] Shutting down...")

        # Clean up in reverse order
        self.audio_capture.stop()
        await self.stt.close()
        self.audio_output.stop()

        print("[SYSTEM] Shutdown complete.")

    async def run_pipeline(self):
        """Main pipeline loop processing sentences."""
        while self.is_running:
            # Check if a complete sentence is ready
            if self.buffer.is_ready():
                sentence = self.buffer.get_next_sentence()
                if sentence:
                    await self._process_sentence(sentence)

            # Small delay to avoid busy waiting
            await asyncio.sleep(0.1)

    async def _process_sentence(self, korean_text: str):
        """Process a single sentence through the translation pipeline.

        Args:
            korean_text: Korean text to translate and speak
        """
        # Start latency measurement
        start_time = time.time()

        # Display original Korean text
        print(f"[STT] {korean_text}")

        # Translate
        translate_start = time.time()
        translated = await self.translator.translate(korean_text)
        translate_time = time.time() - translate_start

        if not translated:
            print("[ERROR] Translation failed, skipping sentence\n")
            return

        print(f"[TRS] {translated}")

        # Synthesize speech
        tts_start = time.time()
        audio_data = await self.tts.synthesize(translated)
        tts_time = time.time() - tts_start

        if not audio_data:
            print("[ERROR] TTS failed, skipping sentence\n")
            return

        # Play audio
        print("[TTS] Playing audio...")
        playback_start = time.time()
        await self.audio_output.play(audio_data)
        playback_time = time.time() - playback_start

        # Calculate total latency
        total_time = time.time() - start_time

        # Log latency breakdown
        print(
            f"[LATENCY] Total: {total_time:.2f}s "
            f"(Translate: {translate_time:.2f}s, "
            f"TTS: {tts_time:.2f}s, "
            f"Playback: {playback_time:.2f}s)\n"
        )

    async def handle_keyboard(self):
        """Handle keyboard input in a non-blocking way."""
        loop = asyncio.get_event_loop()

        while self.is_running:
            # Read from stdin without blocking (simple polling approach)
            try:
                # Use asyncio to run blocking stdin read in executor
                key = await loop.run_in_executor(
                    None, sys.stdin.read, 1
                )

                if key == 'q':
                    print("\n[SYSTEM] Quit command received.")
                    self.is_running = False
                    break
                elif key == 'l':
                    self.toggle_language()
                elif key == 'c':
                    self.buffer.clear()
                    print("\n[SYSTEM] Buffer cleared.\n")

            except Exception:
                # Ignore errors from stdin
                pass

            await asyncio.sleep(0.1)


async def main():
    """Main entry point for VoiceBridge."""
    parser = argparse.ArgumentParser(
        description="VoiceBridge - Real-Time Voice Translation Tool"
    )
    parser.add_argument(
        "--target",
        choices=["en", "de"],
        default="en",
        help="Target language: en (English) or de (German)",
    )
    parser.add_argument(
        "--input-device",
        type=int,
        help="Input device ID (use verify_setup.py to list devices)",
    )
    parser.add_argument(
        "--output-device",
        type=int,
        help="Output device ID (use verify_setup.py to list devices)",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = Config.load_from_env()
        config.target_language = args.target
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create controller
    controller = Controller(
        config,
        input_device=args.input_device,
        output_device=args.output_device,
    )

    try:
        # Start the pipeline
        await controller.start()

        # Run pipeline and keyboard handler concurrently
        await asyncio.gather(
            controller.run_pipeline(),
            controller.handle_keyboard(),
        )

    except KeyboardInterrupt:
        print("\n[SYSTEM] Interrupt received.")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
    finally:
        await controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
