# VoiceBridge - Implementation Plan

## Project Setup
- [x] Create project file structure (src/, tests/, configs)
- [x] Create requirements.txt with all dependencies
- [x] Create .env.example with placeholder keys
- [x] Create .gitignore (exclude .env, __pycache__, venv, etc.)
- [x] Initialize git repository

## Module 1: Configuration
- [x] Build config.py -- load .env, validate required keys, expose settings
- [x] Add device listing utility (list available audio input/output devices)

## Module 2: Audio Capture
- [x] Build audio_capture.py -- capture mic input using sounddevice
- [x] Support configurable input device selection
- [x] Stream audio in chunks suitable for Deepgram (16-bit PCM, 16kHz, mono)

## Module 3: Speech-to-Text
- [x] Build stt_engine.py -- Deepgram streaming WebSocket integration
- [x] Handle interim vs final transcripts
- [x] Handle connection errors and auto-reconnect

## Module 4: Sentence Buffer
- [x] Build sentence_buffer.py -- accumulate partials, emit on finals
- [x] Discard empty/whitespace transcripts
- [x] Support clear() for user-initiated reset

## Module 5: Translation
- [x] Build translator.py -- Claude API integration
- [x] Write system prompt for natural conversational translation
- [x] Support English and German targets
- [x] Handle API errors gracefully

## Module 6: Text-to-Speech
- [x] Build tts_engine.py -- Edge TTS integration
- [x] Convert MP3 output to PCM for playback
- [x] Support English and German voices

## Module 7: Audio Output
- [x] Build audio_output.py -- play PCM audio to selected output device
- [x] Target BlackHole virtual device
- [x] Queue playback (no overlap)

## Module 8: Controller (Main Orchestrator)
- [x] Build main.py -- wire all modules into async pipeline
- [x] Add CLI argument parsing (--target en/de)
- [x] Add terminal display (STT, translation, TTS status)
- [x] Add keyboard commands (quit, language toggle, clear buffer)
- [x] Add latency measurement logging

## Module 9: Setup Verification
- [x] Build verify_setup.py -- check APIs, devices, dependencies

## Testing
- [ ] Write unit tests for sentence_buffer.py
- [ ] Write unit tests for config.py validation
- [ ] Manual end-to-end test: Korean speech -> English audio
- [ ] Manual end-to-end test: Korean speech -> German audio
- [ ] Manual Zoom/Meet test with BlackHole routing

## Documentation
- [x] Write README.md with setup and usage instructions
- [ ] Prepare demo talking points for interview

---

## Review
(To be filled in after implementation is complete)
