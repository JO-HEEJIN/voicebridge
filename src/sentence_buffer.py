"""Sentence buffer for accumulating speech transcripts.

Manages partial and final transcripts, emitting complete sentences for translation.
"""

import asyncio
from typing import Optional


class SentenceBuffer:
    """Accumulates partial transcripts into complete sentences."""

    def __init__(self):
        """Initialize an empty sentence buffer."""
        self._buffer = ""
        self._pending_sentences = asyncio.Queue()

    def add_partial(self, text: str):
        """Update the current partial transcript.

        Args:
            text: Latest partial transcript text (replaces previous partial).
        """
        self._buffer = text

    def add_final(self, text: str):
        """Add a final transcript as a complete sentence.

        Args:
            text: Final transcript text to be queued for translation.
        """
        # Strip and check if non-empty
        cleaned = text.strip()
        if cleaned:
            self._pending_sentences.put_nowait(cleaned)

        # Reset the buffer after processing final
        self._buffer = ""

    def get_next_sentence(self) -> Optional[str]:
        """Get the next complete sentence if available.

        Returns:
            The next sentence from the queue, or None if empty.
        """
        try:
            return self._pending_sentences.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def is_ready(self) -> bool:
        """Check if a complete sentence is available.

        Returns:
            True if at least one sentence is in the queue, False otherwise.
        """
        return not self._pending_sentences.empty()

    def clear(self):
        """Clear the buffer and all pending sentences."""
        self._buffer = ""

        # Drain the queue
        while not self._pending_sentences.empty():
            try:
                self._pending_sentences.get_nowait()
            except asyncio.QueueEmpty:
                break
