#!/usr/bin/env python3
"""Main controller for VoiceBridge - Real-Time Voice Translation Tool.

Push-to-talk pipeline: Space to record → Whisper STT → Claude translate → KittenTTS.
"""

import argparse
import asyncio
import sys
import tty
import termios
import time
from typing import Optional

from config import Config
from audio_capture import AudioCapture
from audio_output import AudioOutput
from stt_engine import STTEngine
from translator import Translator
from tts_engine import TTSEngine


class Controller:
    """Main controller orchestrating the VoiceBridge pipeline."""

    def __init__(self, config: Config, input_device: Optional[int], output_device: Optional[int]):
        self.config = config
        self.target_language = config.target_language
        self.is_running = False
        self._recording = False
        self._last_toggle_time = 0.0
        self._audio_chunks = []  # buffer recorded audio

        # Initialize modules
        self.audio_capture = AudioCapture(
            device_id=input_device,
            sample_rate=config.sample_rate,
        )
        self.audio_output = AudioOutput(device_id=output_device, sample_rate=24000)
        self.stt = STTEngine(model_size="small")
        self.translator = Translator(
            config.anthropic_api_key,
            target_language=self.target_language,
        )
        self.tts = TTSEngine(voice=self._get_voice_for_language(self.target_language))

        self._pending_audio = asyncio.Queue()

    def _get_voice_for_language(self, lang: str) -> str:
        # KittenTTS voices: Bella, Luna, Rosie, Kiki (female), Jasper, Bruno, Hugo, Leo (male)
        return "Bella"

    def _display_header(self):
        lang_name = "English" if self.target_language == "en" else "German"
        print("\n" + "=" * 60)
        print(f"VoiceBridge v1.0 | Target: {lang_name}")
        print("=" * 60)
        print("[Space] Start/Stop recording")
        print("[q] Quit  [l] Language  [c] Clear")
        print("=" * 60)

    def toggle_language(self):
        self.target_language = "de" if self.target_language == "en" else "en"
        self.translator.set_target_language(self.target_language)
        self.tts.set_voice(self._get_voice_for_language(self.target_language))
        lang_name = "English" if self.target_language == "en" else "German"
        print(f"\n[SYSTEM] Language: {lang_name}")

    async def start(self):
        self.is_running = True
        self._display_header()

        loop = asyncio.get_running_loop()

        # Load models (Whisper + KittenTTS)
        await loop.run_in_executor(None, self.stt.load)
        await loop.run_in_executor(None, self.tts.load)

        # Start audio capture
        self.audio_capture.start()
        self.audio_output.start()

        # Collect audio chunks when recording
        self.audio_capture.on_audio_data(self._on_audio)

        print("\nPress [Space] to start speaking...\n")

    def _on_audio(self, chunk: bytes):
        """Buffer audio chunks while recording."""
        if self._recording:
            self._audio_chunks.append(chunk)

    async def stop(self):
        self.is_running = False
        print("\n[SYSTEM] Shutting down...")
        self.audio_capture.stop()
        self.audio_output.stop()
        print("[SYSTEM] Done.")

    def _start_recording(self):
        self._recording = True
        self._audio_chunks.clear()
        print("[REC] Speak now...")

    def _stop_recording(self):
        self._recording = False
        if self._audio_chunks:
            audio_data = b"".join(self._audio_chunks)
            self._audio_chunks.clear()
            self._pending_audio.put_nowait(audio_data)
        else:
            print("[SYSTEM] No audio recorded.\n")
            print("Press [Space] to start speaking...\n")

    async def run_pipeline(self):
        """Process recorded audio through the full pipeline."""
        loop = asyncio.get_running_loop()

        while self.is_running:
            try:
                audio_data = await asyncio.wait_for(
                    self._pending_audio.get(), timeout=0.1
                )
            except asyncio.TimeoutError:
                continue

            start_time = time.time()

            # STT (local Whisper - run in executor to not block)
            stt_start = time.time()
            korean_text = await loop.run_in_executor(
                None, self.stt.transcribe, audio_data
            )
            stt_time = time.time() - stt_start

            if not korean_text:
                print("[SYSTEM] No speech detected.\n")
                print("Press [Space] to start speaking...\n")
                continue

            print(f"[STT] {korean_text}  ({stt_time:.1f}s)")

            # Translate
            translate_start = time.time()
            translated = await self.translator.translate(korean_text)
            translate_time = time.time() - translate_start

            if not translated:
                print("[ERROR] Translation failed\n")
                continue

            print(f"[TRS] {translated}")

            # TTS (local KittenTTS - run in executor)
            tts_start = time.time()
            audio_out = await loop.run_in_executor(
                None, self.tts.synthesize, translated
            )
            tts_time = time.time() - tts_start

            if not audio_out:
                print("[ERROR] TTS failed\n")
                continue

            # Play
            playback_start = time.time()
            await self.audio_output.play(audio_out)
            playback_time = time.time() - playback_start

            total = time.time() - start_time
            print(
                f"[TIME] {total:.1f}s "
                f"(STT:{stt_time:.1f}s T:{translate_time:.1f}s "
                f"TTS:{tts_time:.1f}s P:{playback_time:.1f}s)"
            )
            print("\nPress [Space] to start speaking...\n")

    async def handle_keyboard(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            loop = asyncio.get_running_loop()

            while self.is_running:
                ch = await loop.run_in_executor(None, lambda: sys.stdin.read(1))

                if ch == ' ':
                    now = time.monotonic()
                    if now - self._last_toggle_time < 0.5:
                        continue
                    self._last_toggle_time = now
                    if self._recording:
                        self._stop_recording()
                    else:
                        self._start_recording()
                elif ch == 'q':
                    print("\n[SYSTEM] Quit.")
                    self.is_running = False
                    break
                elif ch == 'l':
                    self.toggle_language()
                elif ch == 'c':
                    self._audio_chunks.clear()
                    print("\n[SYSTEM] Cleared.\n")

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


async def main():
    parser = argparse.ArgumentParser(description="VoiceBridge - Voice Translation")
    parser.add_argument("--target", choices=["en", "de"], default="en")
    parser.add_argument("--input-device", type=int)
    parser.add_argument("--output-device", type=int)
    args = parser.parse_args()

    try:
        config = Config.load_from_env()
        config.target_language = args.target
    except ValueError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    controller = Controller(config, args.input_device, args.output_device)

    try:
        await controller.start()
        await asyncio.gather(
            controller.run_pipeline(),
            controller.handle_keyboard(),
        )
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
    finally:
        await controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
