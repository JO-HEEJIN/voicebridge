# Software Development Plan (SDP)
# Real-Time Voice Translation Tool ("VoiceBridge")

## 1. Project Overview

### 1.1 Purpose
Build a real-time voice translation tool that captures Korean speech, translates it, and outputs natural-sounding English or German audio through a virtual microphone. The tool enables a native Korean speaker to participate in English/German video calls (Zoom, Google Meet) while speaking Korean naturally.

### 1.2 Project Name
**VoiceBridge** -- bridging languages in real-time.

### 1.3 Strategic Context
This project serves dual purposes:
- **Practical utility**: Eliminate cognitive overhead of real-time mental translation during interviews and meetings.
- **Portfolio demonstration**: Showcase "orchestrator-level" AI tool building for the Anthropic FDE interview (Feb 19, 2026), aligning with Dario Amodei's vision of AI with audio interfaces described in "Machines of Loving Grace."

### 1.4 Timeline
- **Start Date**: Feb 13, 2026
- **Deadline**: Feb 19, 2026 (6 days)
- **Development approach**: Rapid prototyping with iterative refinement

---

## 2. Scope

### 2.1 In Scope
- Real-time Korean speech capture from system microphone
- Speech-to-Text (STT) for Korean audio
- Text translation from Korean to English and Korean to German
- Text-to-Speech (TTS) in the target language with natural-sounding voice
- Audio output routing to a virtual microphone device (BlackHole on macOS)
- Simple control interface (start/stop, language toggle)
- End-to-end latency target under 3 seconds (stretch goal: under 2 seconds)

### 2.2 Out of Scope
- GUI-heavy desktop application (terminal/minimal web UI is sufficient)
- Mobile support
- Bidirectional translation (only Korean -> target language)
- Speaker diarization or multi-speaker handling
- Offline mode (internet connection required)
- Windows/Linux support (macOS only for this iteration)

---

## 3. Technical Architecture

### 3.1 Pipeline Overview
```
[Microphone] -> [Audio Capture] -> [STT: Korean] -> [Translation] -> [TTS: Target Lang] -> [Virtual Mic]
```

### 3.2 Technology Stack

| Component         | Choice               | Rationale                                              |
|-------------------|----------------------|--------------------------------------------------------|
| Language          | Python 3.11+         | Fast prototyping, excellent audio/AI library ecosystem |
| Audio Capture     | PyAudio / sounddevice| Direct mic access, low overhead                        |
| STT               | Deepgram API         | Fast streaming STT, strong Korean support, free tier   |
| Translation       | Anthropic Claude API | High quality, Heejin has access, demonstrates product  |
| TTS               | Edge TTS (edge-tts)  | Free, high quality, supports EN/DE, fast               |
| Virtual Mic       | BlackHole (macOS)    | Industry standard virtual audio driver for macOS       |
| Async Runtime     | asyncio              | Non-blocking pipeline for low latency                  |
| Config Management | .env + python-dotenv | Secure API key handling                                |

### 3.3 Alternative Options Considered

**STT Alternatives:**
- Whisper (local): Free but slower for real-time, high CPU usage
- Google Cloud STT: Good but costs add up, complex auth
- Deepgram wins on speed + Korean quality + free tier

**Translation Alternatives:**
- DeepL API: Excellent quality but separate API key needed
- Google Translate API: Good but complex auth setup
- Claude wins because it demonstrates Anthropic product usage and Heejin already has API access

**TTS Alternatives:**
- OpenAI TTS: Higher quality but costs money per request
- Google Cloud TTS: Good but complex auth
- Edge TTS wins because it is completely free and has good quality for EN/DE

### 3.4 Key Design Decisions
1. **Streaming STT over batch**: Deepgram supports streaming, which means we start translating as soon as a sentence is detected rather than waiting for silence.
2. **Sentence-level processing**: Translate complete sentences/phrases for coherent output rather than word-by-word.
3. **Async pipeline**: Each stage runs concurrently to minimize total latency.
4. **Virtual mic routing**: BlackHole acts as a loopback device so Zoom/Meet picks up TTS output as mic input.

---

## 4. Development Phases

### Phase 1: Foundation (Day 1-2)
- Project setup, dependencies, configuration
- Audio capture module (mic input)
- Basic STT integration with Deepgram
- Verify Korean speech recognition works

### Phase 2: Translation Pipeline (Day 2-3)
- Claude API integration for translation
- Sentence boundary detection and buffering
- Korean -> English translation working
- Korean -> German translation working

### Phase 3: TTS and Audio Output (Day 3-4)
- Edge TTS integration
- Audio output to BlackHole virtual device
- End-to-end pipeline test (speak Korean, hear English)

### Phase 4: Integration and Polish (Day 4-5)
- Full async pipeline with proper error handling
- Language toggle (EN/DE switch)
- Latency measurement and optimization
- Simple control interface (terminal-based)

### Phase 5: Testing and Demo Prep (Day 5-6)
- End-to-end testing with Zoom/Google Meet
- Edge case handling (silence, noise, interruptions)
- Demo preparation for interview
- Documentation cleanup

---

## 5. Risk Assessment

| Risk                              | Impact | Probability | Mitigation                                      |
|-----------------------------------|--------|-------------|--------------------------------------------------|
| Latency exceeds 3 seconds        | High   | Medium      | Use streaming STT, optimize pipeline concurrency |
| Deepgram Korean accuracy issues   | High   | Low         | Fall back to Whisper local model                 |
| BlackHole audio routing issues    | Medium | Medium      | Test early, have manual audio routing backup      |
| API rate limits during demo       | High   | Low         | Cache common phrases, implement retry logic       |
| Edge TTS voice sounds unnatural   | Medium | Low         | Test multiple voices, fall back to OpenAI TTS     |

---

## 6. Dependencies and Prerequisites

### 6.1 External Services
- Deepgram API account and key (free tier: 12,000 minutes/year)
- Anthropic Claude API key
- Internet connection during operation

### 6.2 macOS Software
- BlackHole virtual audio driver (free, open source)
- Python 3.11+ installed
- Homebrew for dependency management

### 6.3 Python Packages
- sounddevice (audio capture)
- deepgram-sdk (STT)
- anthropic (translation)
- edge-tts (TTS)
- asyncio (async pipeline)
- python-dotenv (config)
- numpy (audio processing)

---

## 7. Success Criteria

1. Speak a Korean sentence and hear the English translation within 3 seconds
2. Translation quality is coherent and natural (not word-for-word)
3. Works reliably during a 30-minute Zoom call without crashes
4. Language can be switched between English and German mid-session
5. Audio quality is clear enough for professional conversation
6. Demonstrates "orchestrator-level" thinking for FDE interview context

---

## 8. Delivery Artifacts

- Working Python application
- README with setup and usage instructions
- Architecture documentation (these 6 docs)
- Demo script for interview presentation
- tasks/todo.md tracking all implementation progress
