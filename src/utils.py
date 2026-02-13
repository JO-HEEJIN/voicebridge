"""Utility functions for VoiceBridge."""

import sounddevice as sd


def list_audio_devices():
    """List all available audio input and output devices.

    Displays device index, name, and maximum channels for both
    input and output devices.
    """
    devices = sd.query_devices()

    print("\n=== Input Devices ===")
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(
                f"[{idx}] {device['name']} "
                f"(channels: {device['max_input_channels']})"
            )

    print("\n=== Output Devices ===")
    for idx, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            print(
                f"[{idx}] {device['name']} "
                f"(channels: {device['max_output_channels']})"
            )

    print()
