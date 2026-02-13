# VoiceBridge - Implementation Plan

## Project Setup
- [ ] Create project file structure (src/, tests/, configs)
- [ ] Create requirements.txt with all dependencies
- [ ] Create .env.example with placeholder keys
- [ ] Create .gitignore (exclude .env, __pycache__, venv, etc.)
- [ ] Initialize git repository

## Module 1: Configuration
- [ ] Build config.py -- load .env, validate required keys, expose settings
- [ ] Add device listing utility (list available audio input/output devices)

## Module 2: Audio Capture
- [ ] Build audio_capture.py -- capture mic input using sounddevice
- [ ] Support configurable input device selection
- [ ] Stream audio in chunks suitable for Deepgram (16-bit PCM, 16kHz, mono)

## Module 3: Speech-to-Text
- [ ] Build stt_engine.py -- Deepgram streaming WebSocket integration
- [ ] Handle interim vs final transcripts
- [ ] Handle connection errors and auto-reconnect

## Module 4: Sentence Buffer
- [ ] Build sentence_buffer.py -- accumulate partials, emit on finals
- [ ] Discard empty/whitespace transcripts
- [ ] Support clear() for user-initiated reset

## Module 5: Translation
- [ ] Build translator.py -- Claude API integration
- [ ] Write system prompt for natural conversational translation
- [ ] Support English and German targets
- [ ] Handle API errors gracefully

## Module 6: Text-to-Speech
- [ ] Build tts_engine.py -- Edge TTS integration
- [ ] Convert MP3 output to PCM for playback
- [ ] Support English and German voices

## Module 7: Audio Output
- [ ] Build audio_output.py -- play PCM audio to selected output device
- [ ] Target BlackHole virtual device
- [ ] Queue playback (no overlap)

## Module 8: Controller (Main Orchestrator)
- [ ] Build main.py -- wire all modules into async pipeline
- [ ] Add CLI argument parsing (--target en/de)
- [ ] Add terminal display (STT, translation, TTS status)
- [ ] Add keyboard commands (quit, language toggle, clear buffer)
- [ ] Add latency measurement logging

## Module 9: Setup Verification
- [ ] Build verify_setup.py -- check APIs, devices, dependencies

## Testing
- [ ] Write unit tests for sentence_buffer.py
- [ ] Write unit tests for config.py validation
- [ ] Manual end-to-end test: Korean speech -> English audio
- [ ] Manual end-to-end test: Korean speech -> German audio
- [ ] Manual Zoom/Meet test with BlackHole routing

## Documentation
- [ ] Write README.md with setup and usage instructions
- [ ] Prepare demo talking points for interview

---

## Review
(To be filled in after implementation is complete)
