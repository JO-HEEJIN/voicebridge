"""Sentence buffer for accumulating speech transcripts.

Manages partial and final transcripts, emitting complete sentences for translation.
Uses Deepgram's UtteranceEnd event to determine sentence boundaries.
"""

import asyncio
from typing import Optional


class SentenceBuffer:
    """Accumulates partial transcripts into complete sentences."""

    def __init__(self):
        """Initialize an empty sentence buffer."""
        self._accumulated = []
        self._pending_sentences = asyncio.Queue()
        self._partial = ""

    def add_partial(self, text: str):
        """Update the current partial transcript."""
        self._partial = text

    def add_final(self, text: str):
        """Add a final transcript fragment."""
        cleaned = text.strip()
        if cleaned:
            self._accumulated.append(cleaned)

    def flush(self):
        """Flush accumulated finals as one sentence (called on UtteranceEnd)."""
        if not self._accumulated:
            return
        sentence = " ".join(self._accumulated)
        self._accumulated.clear()
        self._partial = ""
        self._pending_sentences.put_nowait(sentence)

    def get_next_sentence(self) -> Optional[str]:
        """Get the next complete sentence if available."""
        try:
            return self._pending_sentences.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def is_ready(self) -> bool:
        """Check if a complete sentence is available."""
        return not self._pending_sentences.empty()

    def clear(self):
        """Clear the buffer and all pending sentences."""
        self._accumulated.clear()
        self._partial = ""
        while not self._pending_sentences.empty():
            try:
                self._pending_sentences.get_nowait()
            except asyncio.QueueEmpty:
                break
