# Test Cases
# VoiceBridge - Real-Time Voice Translation Tool

**Version**: 1.0
**Date**: February 13, 2026
**Based on**: SDP v1.0, UML v1.0, SRS v1.0, BRD v1.0

---

## 1. Test Strategy

Given the 6-day timeline, testing is primarily manual and integration-focused. Unit tests are written only for critical logic (sentence buffering, config validation). The majority of testing is end-to-end, verifying the full pipeline in realistic conditions.

### Test Categories
1. **Unit Tests** -- Isolated module tests (automated, pytest)
2. **Integration Tests** -- Multi-module pipeline tests (manual + scripted)
3. **End-to-End Tests** -- Full pipeline with real audio (manual)
4. **Acceptance Tests** -- Real video call scenario (manual)

---

## 2. Unit Tests

### TC-U01: Config Validation
**Requirement**: FR-08.4
**Module**: config.py

| Step | Action                                      | Expected Result                              |
|------|---------------------------------------------|----------------------------------------------|
| 1    | Load config with all keys present in .env   | Config object created successfully           |
| 2    | Load config with missing DEEPGRAM_API_KEY   | Raises ConfigError with message naming the missing key |
| 3    | Load config with missing ANTHROPIC_API_KEY  | Raises ConfigError with message naming the missing key |
| 4    | Load config with empty .env file            | Raises ConfigError listing all missing keys  |

### TC-U02: Sentence Buffer Logic
**Requirement**: FR-03.1, FR-03.2, FR-03.3
**Module**: sentence_buffer.py

| Step | Action                                      | Expected Result                              |
|------|---------------------------------------------|----------------------------------------------|
| 1    | Add partial transcript "안녕하"             | is_ready() returns False                     |
| 2    | Add final transcript "안녕하세요"            | is_ready() returns True                      |
| 3    | get_next_sentence() after final             | Returns "안녕하세요", buffer is empty         |
| 4    | Add empty string as final transcript        | is_ready() returns False (discarded)         |
| 5    | Add whitespace-only "   " as final          | is_ready() returns False (discarded)         |
| 6    | Add multiple finals before consuming        | Queue holds all, get_next returns first-in   |
| 7    | Call clear()                                | Buffer and queue are emptied                 |

### TC-U03: Translator Prompt Construction
**Requirement**: FR-04.3, FR-04.5
**Module**: translator.py

| Step | Action                                      | Expected Result                              |
|------|---------------------------------------------|----------------------------------------------|
| 1    | Construct prompt for English target          | System prompt includes "natural conversational English" |
| 2    | Construct prompt for German target           | System prompt includes "natural conversational German"  |
| 3    | Verify prompt instructs concise output       | System prompt contains instruction about brevity        |

---

## 3. Integration Tests

### TC-I01: Audio Capture to STT
**Requirements**: FR-01, FR-02

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Start audio capture with default microphone        | No errors, stream is open                    |
| 2    | Speak "테스트입니다" into microphone               | Deepgram returns transcript containing "테스트" |
| 3    | Stay silent for 5 seconds                          | No erroneous transcripts produced            |
| 4    | Speak a long sentence (20+ syllables)              | Full sentence transcribed without truncation |

### TC-I02: STT to Translation
**Requirements**: FR-02, FR-03, FR-04

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Feed Korean text "저는 AI 엔지니어입니다" to translator | Returns English: "I am an AI engineer" or equivalent |
| 2    | Feed Korean text to translator with target=German  | Returns German translation                   |
| 3    | Feed empty string to translator                    | Returns empty string or is skipped           |

### TC-I03: Translation to TTS
**Requirements**: FR-04, FR-05

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Feed "Hello, I am an AI engineer" to TTS           | Returns audio bytes, non-empty               |
| 2    | Feed German text to TTS with German voice          | Returns audio bytes with German pronunciation|
| 3    | Play returned audio bytes through speaker           | Audio is intelligible and natural-sounding   |

### TC-I04: TTS to Audio Output
**Requirements**: FR-05, FR-06

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Play TTS audio to BlackHole device                 | Audio routing confirmed (test with Audacity or QuickTime) |
| 2    | Play two sentences sequentially                    | Second plays after first completes, no overlap |

---

## 4. End-to-End Tests

### TC-E01: Full Pipeline - Korean to English
**Requirements**: FR-01 through FR-07

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Start VoiceBridge with target=English              | Terminal shows "Listening" status             |
| 2    | Speak: "안녕하세요, 저는 AI 엔지니어입니다"        | Terminal shows Korean transcript              |
| 3    | Wait                                                | Terminal shows English translation            |
| 4    | Wait                                                | English audio plays through BlackHole         |
| 5    | Measure time from speech end to audio start        | Under 3 seconds                              |

### TC-E02: Full Pipeline - Korean to German
**Requirements**: Same as TC-E01 but with German target

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Start VoiceBridge with target=German               | Terminal shows "Listening" status             |
| 2    | Speak: "저는 독일에서 일하고 싶습니다"              | Terminal shows Korean transcript              |
| 3    | Wait                                                | Terminal shows German translation             |
| 4    | Wait                                                | German audio plays through BlackHole          |

### TC-E03: Language Toggle Mid-Session
**Requirements**: FR-07.3

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Start with target=English                          | English mode active                          |
| 2    | Speak a Korean sentence                            | English translation and audio output          |
| 3    | Press language toggle key                          | Terminal shows "Target: German"               |
| 4    | Speak another Korean sentence                      | German translation and audio output           |

### TC-E04: Error Recovery
**Requirements**: NFR-02.1, NFR-02.2

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Disconnect WiFi briefly during operation           | Error logged, no crash                        |
| 2    | Reconnect WiFi                                     | Pipeline resumes automatically                |
| 3    | Speak after recovery                               | Translation works normally                    |

### TC-E05: Extended Session Stability
**Requirements**: NFR-02.1

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Run VoiceBridge continuously for 30 minutes        | No crashes or memory leaks                   |
| 2    | Speak sentences every 1-2 minutes throughout       | All translated correctly                     |
| 3    | Check CPU usage during session                     | Under 30%                                    |
| 4    | Check memory usage during session                  | Under 500 MB                                 |

---

## 5. Acceptance Tests

### TC-A01: Zoom Call Test
**Requirements**: BRD Acceptance Criteria

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Open Zoom, set microphone to BlackHole             | Zoom shows BlackHole as mic input            |
| 2    | Join a test Zoom call (with a friend or second device) | Call connected                            |
| 3    | Start VoiceBridge                                  | Terminal shows "Listening"                    |
| 4    | Speak Korean into physical microphone              | Other party hears English on their end       |
| 5    | Speak 5 different sentences                        | All 5 translated and heard correctly         |
| 6    | Run for 10 minutes of conversation                 | Stable, no dropouts                          |

### TC-A02: Google Meet Call Test
**Requirements**: Same as TC-A01 but with Google Meet

| Step | Action                                             | Expected Result                              |
|------|----------------------------------------------------|----------------------------------------------|
| 1    | Open Google Meet in Chrome                         | Meet loaded                                  |
| 2    | Set microphone to BlackHole in Meet settings       | BlackHole selected                           |
| 3    | Join a test meeting                                | Connected                                    |
| 4    | Start VoiceBridge, speak Korean                    | Other party hears English                    |

---

## 6. Test Data

### Korean Test Sentences (varying complexity)

| ID  | Korean                                          | Expected English (approximate)                  |
|-----|------------------------------------------------|------------------------------------------------|
| S01 | 안녕하세요                                      | Hello                                           |
| S02 | 저는 AI 엔지니어입니다                          | I am an AI engineer                             |
| S03 | 이 프로젝트에서 가장 어려웠던 점은 지연 시간을 줄이는 것이었습니다 | The hardest part of this project was reducing latency |
| S04 | 저는 한국에서 태어나서 미국에서 컴퓨터 과학을 공부했습니다 | I was born in Korea and studied computer science in the US |
| S05 | 클로드 API를 사용해서 번역 품질을 높였습니다     | I used the Claude API to improve translation quality |
| S06 | 이 도구는 다리오 아모데이의 비전을 실제로 구현한 것입니다 | This tool is a practical implementation of Dario Amodei's vision |
| S07 | 질문이 있으시면 말씀해 주세요                    | If you have any questions, please let me know   |

---

## 7. Test Environment

- **Hardware**: MacBook (Apple Silicon preferred)
- **OS**: macOS 13+ (Ventura or later)
- **Audio**: Built-in microphone + BlackHole 2ch installed
- **Network**: Stable WiFi or Ethernet
- **Software**: Python 3.11+, Zoom, Google Meet (Chrome)
- **API access**: Valid Deepgram and Anthropic API keys
