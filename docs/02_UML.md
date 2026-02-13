# UML Diagrams
# VoiceBridge - Real-Time Voice Translation Tool

All diagrams below are in Mermaid syntax and can be rendered in any Mermaid-compatible viewer (GitHub, VS Code with Mermaid extension, mermaid.live).

---

## 1. System Context Diagram

Shows VoiceBridge in relation to external systems and actors.

```mermaid
graph TB
    User["User (Korean Speaker)"]
    VB["VoiceBridge Application"]
    DG["Deepgram API<br/>(Speech-to-Text)"]
    CL["Claude API<br/>(Translation)"]
    ET["Edge TTS<br/>(Text-to-Speech)"]
    BH["BlackHole<br/>(Virtual Audio Driver)"]
    VC["Video Call App<br/>(Zoom / Google Meet)"]
    INT["Interviewer / Listener"]

    User -->|"Korean speech"| VB
    VB -->|"Audio stream"| DG
    DG -->|"Korean text"| VB
    VB -->|"Korean text"| CL
    CL -->|"English/German text"| VB
    VB -->|"Translated text"| ET
    ET -->|"Audio (EN/DE)"| VB
    VB -->|"TTS audio output"| BH
    BH -->|"Virtual mic input"| VC
    VC -->|"Audio stream"| INT
```

---

## 2. Component Diagram

Shows internal modules of VoiceBridge and their relationships.

```mermaid
graph LR
    subgraph VoiceBridge
        AC["AudioCapture<br/>Module"]
        STT["STTEngine<br/>(Deepgram)"]
        SB["SentenceBuffer"]
        TR["Translator<br/>(Claude API)"]
        TTS["TTSEngine<br/>(Edge TTS)"]
        AO["AudioOutput<br/>(BlackHole)"]
        CTRL["Controller<br/>(Main Loop)"]
        CFG["Config<br/>(.env loader)"]
    end

    AC -->|"raw audio chunks"| STT
    STT -->|"partial/final transcripts"| SB
    SB -->|"complete sentences"| TR
    TR -->|"translated text"| TTS
    TTS -->|"audio bytes"| AO

    CTRL --> AC
    CTRL --> STT
    CTRL --> TR
    CTRL --> TTS
    CTRL --> AO
    CFG --> CTRL
```

---

## 3. Sequence Diagram

Shows the end-to-end flow for a single spoken sentence.

```mermaid
sequenceDiagram
    participant User
    participant AudioCapture
    participant Deepgram
    participant SentenceBuffer
    participant Claude
    participant EdgeTTS
    participant BlackHole
    participant ZoomMeet

    User->>AudioCapture: Speaks Korean sentence
    AudioCapture->>Deepgram: Stream audio chunks
    Deepgram-->>SentenceBuffer: Partial transcript (interim)
    Deepgram->>SentenceBuffer: Final transcript (sentence complete)
    SentenceBuffer->>Claude: "Translate to English: [Korean text]"
    Claude->>SentenceBuffer: "[English translation]"
    SentenceBuffer->>EdgeTTS: Generate speech for English text
    EdgeTTS->>BlackHole: Output audio bytes
    BlackHole->>ZoomMeet: Virtual mic input
    ZoomMeet->>User: Interviewer hears English
```

---

## 4. Class Diagram

Shows the main classes/modules and their responsibilities.

```mermaid
classDiagram
    class Config {
        +str deepgram_api_key
        +str anthropic_api_key
        +str target_language
        +int sample_rate
        +str input_device
        +str output_device
        +load_from_env()
    }

    class AudioCapture {
        -stream: InputStream
        -sample_rate: int
        -channels: int
        -device_id: int
        +start()
        +stop()
        +get_audio_chunk() bytes
        +on_audio_data(callback)
    }

    class STTEngine {
        -client: DeepgramClient
        -connection: LiveConnection
        -language: str
        +connect()
        +send_audio(chunk: bytes)
        +on_transcript(callback)
        +close()
    }

    class SentenceBuffer {
        -buffer: str
        -pending_sentences: Queue
        +add_partial(text: str)
        +add_final(text: str)
        +get_next_sentence() str
        +is_ready() bool
    }

    class Translator {
        -client: AnthropicClient
        -target_lang: str
        -system_prompt: str
        +translate(text: str, target: str) str
        +set_target_language(lang: str)
    }

    class TTSEngine {
        -voice: str
        -rate: str
        +synthesize(text: str) bytes
        +set_voice(voice_id: str)
        +get_available_voices() list
    }

    class AudioOutput {
        -stream: OutputStream
        -device_id: int
        -sample_rate: int
        +start()
        +stop()
        +play(audio_data: bytes)
    }

    class Controller {
        -config: Config
        -audio_capture: AudioCapture
        -stt: STTEngine
        -buffer: SentenceBuffer
        -translator: Translator
        -tts: TTSEngine
        -audio_output: AudioOutput
        -is_running: bool
        -target_language: str
        +start()
        +stop()
        +toggle_language()
        +run_pipeline()
    }

    Controller --> Config
    Controller --> AudioCapture
    Controller --> STTEngine
    Controller --> SentenceBuffer
    Controller --> Translator
    Controller --> TTSEngine
    Controller --> AudioOutput
    STTEngine --> SentenceBuffer
    SentenceBuffer --> Translator
    Translator --> TTSEngine
    TTSEngine --> AudioOutput
```

---

## 5. State Diagram

Shows the application states during operation.

```mermaid
stateDiagram-v2
    [*] --> Idle: Application starts
    Idle --> Initializing: User presses Start
    Initializing --> Listening: All services connected
    Initializing --> Error: Connection failed

    Listening --> Processing: Speech detected
    Processing --> Translating: STT complete (sentence ready)
    Translating --> Synthesizing: Translation complete
    Synthesizing --> Playing: TTS audio ready
    Playing --> Listening: Audio playback complete

    Listening --> Paused: User presses Pause
    Paused --> Listening: User presses Resume

    Listening --> Idle: User presses Stop
    Processing --> Idle: User presses Stop
    Error --> Idle: User acknowledges error
    Error --> Initializing: User retries

    state Processing {
        [*] --> BufferingAudio
        BufferingAudio --> RecognizingSpeech
        RecognizingSpeech --> SentenceComplete
    }
```

---

## 6. Deployment Diagram

Shows how VoiceBridge runs on the user's macOS system.

```mermaid
graph TB
    subgraph "macOS System"
        subgraph "VoiceBridge Process (Python)"
            Main["main.py<br/>(Controller)"]
            Mods["Modules<br/>(capture, stt, translate, tts, output)"]
        end

        subgraph "Audio Layer"
            Mic["Physical Microphone<br/>(Built-in / External)"]
            BH["BlackHole Virtual Device<br/>(2ch)"]
            MultiOut["Multi-Output Device<br/>(Optional: hear own output)"]
        end

        subgraph "Video Call"
            Zoom["Zoom / Google Meet<br/>(Uses BlackHole as mic input)"]
        end
    end

    subgraph "Cloud Services"
        DG["Deepgram API"]
        AN["Anthropic Claude API"]
        MS["Microsoft Edge TTS"]
    end

    Mic --> Main
    Main --> DG
    DG --> Main
    Main --> AN
    AN --> Main
    Main --> MS
    MS --> Main
    Main --> BH
    BH --> Zoom
```

---

## Notes on Architecture Decisions

1. **Linear pipeline**: The design is intentionally a simple linear pipeline rather than a complex event-driven architecture. This keeps the code simple and debuggable within the 6-day timeline.

2. **SentenceBuffer as coordinator**: The buffer sits between STT and translation to accumulate partial transcripts into complete sentences before sending them for translation. This prevents fragmented or incoherent translations.

3. **Controller as orchestrator**: A single Controller class manages the entire pipeline lifecycle. This aligns with the "orchestrator-level" developer skill being demonstrated.

4. **No persistent state**: The application is stateless between sessions. No database, no file storage. This keeps things simple.
