# Software Requirements Specification (SRS)
# VoiceBridge - Real-Time Voice Translation Tool

**Version**: 1.0
**Date**: February 13, 2026
**Based on**: SDP v1.0, UML v1.0

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements for VoiceBridge, a real-time voice translation tool that converts live Korean speech into English or German audio output through a virtual microphone device.

### 1.2 Intended Audience
- Developer (Heejin Jo) for implementation reference
- Interview reviewers evaluating system design capability
- Future contributors if the project is open-sourced

### 1.3 System Overview
VoiceBridge is a macOS command-line application written in Python that chains together Speech-to-Text, machine translation, and Text-to-Speech services into a real-time audio pipeline, routing the final output through BlackHole virtual audio driver for use in video conferencing applications.

---

## 2. Functional Requirements

### FR-01: Audio Capture
- **FR-01.1**: The system shall capture audio from the user's selected microphone device.
- **FR-01.2**: The system shall support configurable sample rate (default: 16000 Hz).
- **FR-01.3**: The system shall capture audio in mono channel format.
- **FR-01.4**: The system shall stream audio in chunks (not batch) for low latency.
- **FR-01.5**: The system shall allow the user to select which input device to use at startup.

### FR-02: Speech-to-Text (STT)
- **FR-02.1**: The system shall transcribe Korean speech to Korean text in real-time.
- **FR-02.2**: The system shall use Deepgram's streaming API for transcription.
- **FR-02.3**: The system shall distinguish between interim (partial) and final transcripts.
- **FR-02.4**: The system shall handle silence periods without producing erroneous output.
- **FR-02.5**: The system shall reconnect automatically if the STT connection drops.

### FR-03: Sentence Buffering
- **FR-03.1**: The system shall accumulate partial transcripts into complete sentences.
- **FR-03.2**: The system shall emit a sentence for translation only when the STT engine signals a final transcript or a sentence-ending punctuation is detected.
- **FR-03.3**: The system shall discard empty or whitespace-only transcripts.
- **FR-03.4**: The buffer shall be clearable by the user (e.g., if they misspoke).

### FR-04: Translation
- **FR-04.1**: The system shall translate Korean text to English using the Anthropic Claude API.
- **FR-04.2**: The system shall translate Korean text to German using the same API.
- **FR-04.3**: The system shall use a system prompt that instructs Claude to produce natural, conversational translations (not literal/word-for-word).
- **FR-04.4**: The system shall handle translation errors gracefully (log error, skip sentence, continue pipeline).
- **FR-04.5**: The translation prompt shall instruct Claude to keep the output concise, matching the brevity of spoken language rather than written prose.

### FR-05: Text-to-Speech (TTS)
- **FR-05.1**: The system shall convert translated English text to English speech audio.
- **FR-05.2**: The system shall convert translated German text to German speech audio.
- **FR-05.3**: The system shall use Edge TTS for speech synthesis.
- **FR-05.4**: The system shall use a natural-sounding male or female voice (configurable).
- **FR-05.5**: The TTS output shall be in a format playable through the audio output module (PCM/WAV).

### FR-06: Audio Output
- **FR-06.1**: The system shall play TTS audio through the BlackHole virtual audio device.
- **FR-06.2**: The system shall not overlap audio playback (queue sentences sequentially).
- **FR-06.3**: The system shall support configurable output device selection.

### FR-07: User Controls
- **FR-07.1**: The system shall provide a start command to begin the translation pipeline.
- **FR-07.2**: The system shall provide a stop command to halt the pipeline cleanly.
- **FR-07.3**: The system shall provide a command to toggle between English and German target languages during operation.
- **FR-07.4**: The system shall display the current state (listening, translating, speaking) in the terminal.
- **FR-07.5**: The system shall display each step's output (Korean text, translated text) in the terminal for debugging and verification.

### FR-08: Configuration
- **FR-08.1**: The system shall load API keys from a .env file.
- **FR-08.2**: The system shall never log, print, or expose API keys in output.
- **FR-08.3**: The system shall provide a .env.example file with placeholder values.
- **FR-08.4**: The system shall validate that required API keys are present at startup and exit with a clear error message if missing.

---

## 3. Non-Functional Requirements

### NFR-01: Latency
- **NFR-01.1**: End-to-end latency (speech input to audio output) shall be under 3 seconds for a typical sentence (10-15 Korean syllables).
- **NFR-01.2**: Stretch goal: under 2 seconds end-to-end.
- **NFR-01.3**: The system shall measure and log per-stage latency for optimization.

### NFR-02: Reliability
- **NFR-02.1**: The system shall operate continuously for at least 30 minutes without crashing.
- **NFR-02.2**: The system shall recover gracefully from transient API errors (network blip, rate limit) without requiring a restart.
- **NFR-02.3**: The system shall log errors to stderr without interrupting the audio pipeline.

### NFR-03: Security
- **NFR-03.1**: API keys shall be stored only in .env files, never in source code.
- **NFR-03.2**: The .gitignore file shall exclude .env files.
- **NFR-03.3**: No audio data shall be persisted to disk during normal operation.
- **NFR-03.4**: The system shall not transmit audio to any service other than the configured STT provider.

### NFR-04: Usability
- **NFR-04.1**: Setup shall require no more than 5 terminal commands.
- **NFR-04.2**: The README shall include step-by-step setup instructions for macOS.
- **NFR-04.3**: Error messages shall be human-readable and suggest corrective actions.

### NFR-05: Performance
- **NFR-05.1**: CPU usage shall remain under 30% on an M-series MacBook during operation.
- **NFR-05.2**: Memory usage shall remain under 500 MB during operation.
- **NFR-05.3**: The application shall start and be ready to listen within 5 seconds.

### NFR-06: Maintainability
- **NFR-06.1**: Each pipeline stage shall be implemented as a separate Python module.
- **NFR-06.2**: Swapping an STT, translation, or TTS provider shall require changes to only one module.
- **NFR-06.3**: Code shall follow PEP 8 style guidelines.

### NFR-07: Compatibility
- **NFR-07.1**: The system shall run on macOS 13 (Ventura) or later.
- **NFR-07.2**: The system shall be compatible with Python 3.11 or later.
- **NFR-07.3**: The system shall work with Zoom, Google Meet, and any application that accepts a virtual microphone as input.

---

## 4. Interface Requirements

### 4.1 External API Interfaces

**Deepgram Streaming API**
- Protocol: WebSocket
- Auth: API key in header
- Input: Raw audio bytes (16-bit PCM, 16kHz, mono)
- Output: JSON with transcript, is_final flag, confidence score

**Anthropic Claude API**
- Protocol: HTTPS REST
- Auth: API key in header
- Input: JSON message with system prompt + Korean text
- Output: JSON with translated text
- Model: claude-sonnet-4-20250514 (fast, cost-effective for short texts)

**Edge TTS**
- Protocol: WebSocket (handled by edge-tts library)
- Auth: None required
- Input: Text string + voice identifier
- Output: Audio bytes (MP3 format, converted to PCM for playback)

### 4.2 Audio Interfaces

**Input**: System microphone (physical hardware)
- Format: 16-bit PCM, 16000 Hz, mono

**Output**: BlackHole virtual audio device
- Format: 16-bit PCM, 24000 Hz (or matching TTS output rate), mono

### 4.3 User Interface

Terminal-based interface with the following display:
```
VoiceBridge v1.0 | Target: English | Status: Listening
---
[STT] 안녕하세요, 저는 AI 엔지니어입니다
[TRS] Hello, I am an AI engineer
[TTS] Playing audio...
---
Commands: [q]uit | [l]anguage toggle | [c]lear buffer
```

---

## 5. Constraints

1. **Budget**: Prefer free-tier APIs. Deepgram free tier provides 12,000 minutes/year. Claude API cost should be minimal (short text translations).
2. **Timeline**: 6 days to working prototype. No time for complex UI or advanced features.
3. **Platform**: macOS only. BlackHole is macOS-specific.
4. **Network**: Requires stable internet connection. No offline fallback in v1.0.
5. **Single speaker**: Designed for one speaker at a time. No multi-party translation.

---

## 6. Assumptions

1. The user has a working microphone on their Mac.
2. BlackHole virtual audio driver is installed and configured.
3. The user has valid Deepgram and Anthropic API keys.
4. The user's internet connection is stable with reasonable latency to US-based API servers.
5. The video call application (Zoom/Meet) can be configured to use BlackHole as the microphone input.
