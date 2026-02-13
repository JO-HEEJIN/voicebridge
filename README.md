# VoiceBridge

Real-time voice translation tool that converts live Korean speech into English or German audio output through a virtual microphone.

## Overview

VoiceBridge enables Korean speakers to participate in English or German video calls (Zoom, Google Meet) while speaking naturally in Korean. The tool captures your speech, translates it in real-time, and outputs natural-sounding speech in the target language through a virtual audio device.

**Key Features:**
- Real-time Korean speech-to-text using Deepgram
- Natural translation using Anthropic Claude API
- High-quality text-to-speech with Edge TTS
- Optimized pipeline with Haiku translation and utterance-based buffering
- Live language switching between English and German
- Routes output through BlackHole virtual audio driver for video call integration

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Microphone │────▶│ AudioCapture │────▶│   Deepgram STT  │
└─────────────┘     └──────────────┘     └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │ SentenceBuffer  │
                                         └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │  Claude API     │
                                         │  (Translation)  │
                                         └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │   Edge TTS      │
                                         └─────────────────┘
                                                   │
                                                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Zoom/Meet  │◀────│  BlackHole   │◀────│  AudioOutput    │
└─────────────┘     └──────────────┘     └─────────────────┘
```

## Prerequisites

### System Requirements
- **macOS** 13 (Ventura) or later
- **Python** 3.11+ (tested with 3.13)
- **BlackHole** virtual audio driver ([download](https://existential.audio/blackhole/))
- **ffmpeg** for audio conversion (`brew install ffmpeg`)

### API Keys
- **Deepgram API Key** - [Sign up](https://deepgram.com/) (12,000 min/year free tier)
- **Anthropic API Key** - [Get access](https://console.anthropic.com/)

## Quick Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd voice-translator

# Create virtual environment (use python3.11+ or python3.13)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Add your keys to `.env`:
```
DEEPGRAM_API_KEY=your_deepgram_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Verify Setup

```bash
python src/verify_setup.py
```

This will check:
- Python version
- Required packages
- API key configuration
- Audio devices (including BlackHole)
- ffmpeg availability

## Usage

### Basic Usage

Start VoiceBridge with English as the target language:

```bash
python src/main.py --target en
```

For German translation:

```bash
python src/main.py --target de
```

### Specifying Audio Devices

List available audio devices:

```bash
python -c "from src.utils import list_audio_devices; list_audio_devices()"
```

Run with specific devices:

```bash
python src/main.py --target en --input-device 1 --output-device 4
```

### Keyboard Commands

While VoiceBridge is running:
- **`q`** - Quit the application
- **`l`** - Toggle language (English ↔ German)
- **`c`** - Clear sentence buffer (if you misspoke)

### Using with Zoom/Google Meet

1. Start VoiceBridge with your desired target language
2. In Zoom/Meet, go to audio settings
3. Select **BlackHole** as your microphone input
4. Speak Korean into your physical microphone
5. The translated audio will be heard by other participants

**Tip:** Use headphones to avoid audio feedback loops.

## How It Works

### Pipeline Flow

1. **Audio Capture** - Captures live microphone input (16-bit PCM, 16kHz, mono)
2. **Speech-to-Text** - Deepgram streaming API transcribes Korean speech in real-time
3. **Sentence Buffering** - Accumulates partial transcripts into complete sentences
4. **Translation** - Claude API translates Korean text to natural English/German
5. **Text-to-Speech** - Edge TTS synthesizes natural-sounding speech
6. **Audio Output** - Plays translated audio through BlackHole virtual device

### Latency Optimization

VoiceBridge is designed for low latency:
- Streaming STT with Deepgram's `utterance_end_ms` for smart sentence boundaries
- Claude Haiku for fast translation (~0.5-1s)
- Async pipeline with non-blocking audio playback
- Sentence-level batching (balances coherence and speed)
- Latency logging on each translation

Typical end-to-end latency: **3-5 seconds** including audio playback.

## Project Structure

```
voice-translator/
├── src/
│   ├── main.py              # Main controller and CLI entry point
│   ├── config.py            # Configuration management
│   ├── utils.py             # Utility functions
│   ├── audio_capture.py     # Microphone input module
│   ├── audio_output.py      # Audio playback module
│   ├── stt_engine.py        # Deepgram STT integration
│   ├── sentence_buffer.py   # Transcript accumulation
│   ├── translator.py        # Claude API translation
│   ├── tts_engine.py        # Edge TTS synthesis
│   └── verify_setup.py      # Setup verification script
├── docs/                    # Architecture and design documentation
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
└── README.md                # This file
```

## Troubleshooting

### "DEEPGRAM_API_KEY is required"
- Ensure you've created a `.env` file from `.env.example`
- Verify your API key is correct and not empty

### "BlackHole not found"
- Install BlackHole from [existential.audio/blackhole](https://existential.audio/blackhole/)
- Restart your Mac after installation
- Verify it appears in System Settings > Sound

### "ffmpeg not found"
- Install via Homebrew: `brew install ffmpeg`
- Verify installation: `ffmpeg -version`

### Audio feedback or echo
- Use headphones when testing
- Ensure BlackHole is set as output in VoiceBridge
- Check that your video call app is using BlackHole as microphone input

### High latency (> 5 seconds)
- Check your internet connection
- Verify you're not hitting API rate limits
- Run latency tests with shorter sentences
- Consider upgrading to faster API tiers

### No audio output
- Run `verify_setup.py` to check audio devices
- Verify BlackHole is installed and recognized
- Check output device ID with `list_audio_devices()`
- Try specifying `--output-device` explicitly

## Development

### Running Tests

```bash
# Unit tests (when implemented)
pytest tests/

# Manual end-to-end test
python src/main.py --target en
# Speak Korean and verify English output
```

### Code Style

This project follows PEP 8 style guidelines. Format code with:

```bash
black src/
```

## License

This project is licensed under the MIT License.

## Acknowledgments

- **Deepgram** for excellent Korean STT support
- **Anthropic** for high-quality Claude translation API
- **Microsoft Edge TTS** for free, natural-sounding voices
- **BlackHole** for macOS virtual audio routing

---

**Built with ❤️ for the Anthropic FDE interview by Heejin Jo**
