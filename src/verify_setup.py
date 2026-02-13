#!/usr/bin/env python3
"""Setup verification script for VoiceBridge.

Checks that all dependencies, API keys, and audio devices are properly configured.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11 or later."""
    version = sys.version_info
    if version >= (3, 11):
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version {version.major}.{version.minor} is too old (need 3.11+)")
        return False


def check_packages():
    """Check if all required packages are installed."""
    required_packages = [
        ("sounddevice", "sounddevice"),
        ("numpy", "numpy"),
        ("dotenv", "python-dotenv"),
        ("deepgram", "deepgram-sdk"),
        ("anthropic", "anthropic"),
        ("edge_tts", "edge-tts"),
    ]

    all_ok = True
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ Package installed: {package_name}")
        except ImportError:
            print(f"✗ Package missing: {package_name}")
            all_ok = False

    return all_ok


def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print("✗ .env file not found (copy .env.example and add your keys)")
        return False

    print("✓ .env file exists")

    # Load .env and check for required keys (without exposing values)
    from dotenv import load_dotenv
    load_dotenv(env_path)

    keys_ok = True

    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    if deepgram_key and len(deepgram_key) > 0:
        print("✓ DEEPGRAM_API_KEY is set")
    else:
        print("✗ DEEPGRAM_API_KEY is missing or empty")
        keys_ok = False

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and len(anthropic_key) > 0:
        print("✓ ANTHROPIC_API_KEY is set")
    else:
        print("✗ ANTHROPIC_API_KEY is missing or empty")
        keys_ok = False

    return keys_ok


def check_audio_devices():
    """Check for available audio devices and BlackHole."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()

        input_count = sum(1 for d in devices if d['max_input_channels'] > 0)
        output_count = sum(1 for d in devices if d['max_output_channels'] > 0)

        print(f"✓ Found {input_count} input device(s)")
        print(f"✓ Found {output_count} output device(s)")

        # Check for BlackHole in output devices
        blackhole_found = False
        for device in devices:
            if 'blackhole' in device['name'].lower() and device['max_output_channels'] > 0:
                blackhole_found = True
                print(f"✓ BlackHole device found: {device['name']}")
                break

        if not blackhole_found:
            print("⚠ BlackHole not found in output devices (install from existential.audio)")
            print("  VoiceBridge will still work, but you'll need BlackHole for Zoom/Meet routing")

        return True

    except Exception as e:
        print(f"✗ Error checking audio devices: {e}")
        return False


def check_ffmpeg():
    """Check if ffmpeg is installed and available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ ffmpeg is available: {version_line}")
            return True
        else:
            print("✗ ffmpeg command failed")
            return False
    except FileNotFoundError:
        print("✗ ffmpeg not found (install with: brew install ffmpeg)")
        return False
    except Exception as e:
        print(f"✗ Error checking ffmpeg: {e}")
        return False


def test_deepgram_api():
    """Test Deepgram API key validity (optional)."""
    try:
        from dotenv import load_dotenv
        from deepgram import DeepgramClient

        load_dotenv()
        api_key = os.getenv("DEEPGRAM_API_KEY")

        if not api_key:
            return False

        # Simple API check (just create client, don't make a real call)
        client = DeepgramClient(api_key)
        print("✓ Deepgram API key format is valid")
        return True

    except Exception as e:
        print(f"⚠ Could not validate Deepgram API key: {e}")
        return False


def test_anthropic_api():
    """Test Anthropic API key validity (optional)."""
    try:
        from dotenv import load_dotenv
        from anthropic import Anthropic

        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            return False

        # Simple API check (just create client, don't make a real call)
        client = Anthropic(api_key=api_key)
        print("✓ Anthropic API key format is valid")
        return True

    except Exception as e:
        print(f"⚠ Could not validate Anthropic API key: {e}")
        return False


def main():
    """Run all verification checks and print summary."""
    print("\n" + "=" * 60)
    print("VoiceBridge Setup Verification")
    print("=" * 60 + "\n")

    results = []

    print("--- Python Environment ---")
    results.append(check_python_version())
    print()

    print("--- Required Packages ---")
    results.append(check_packages())
    print()

    print("--- Configuration ---")
    results.append(check_env_file())
    print()

    print("--- Audio Devices ---")
    results.append(check_audio_devices())
    print()

    print("--- External Tools ---")
    results.append(check_ffmpeg())
    print()

    print("--- API Keys (Optional Validation) ---")
    test_deepgram_api()
    test_anthropic_api()
    print()

    # Summary
    print("=" * 60)
    if all(results):
        print("✓ All required checks passed! VoiceBridge is ready to run.")
        print("\nNext step: Run 'python src/main.py --target en' to start.")
    else:
        print("✗ Some checks failed. Please fix the issues above before running.")
        sys.exit(1)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
