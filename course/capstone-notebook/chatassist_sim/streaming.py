"""StreamingResponse — SSE-formatted streaming for the ChatAssist simulator."""

import json
import time
import uuid
from typing import List, Optional

from .response import SimulatedResponse


# Default content used when no specific pool text is provided.
_DEFAULT_STREAMING_TEXT = (
    "An API is a set of rules and protocols that allows different software "
    "applications to communicate with each other and exchange data."
)


def _split_into_word_chunks(text: str) -> List[str]:
    """Split *text* into word-level chunks preserving whitespace.

    Each chunk is a word optionally preceded by a space so that
    ``"".join(chunks) == text``.
    """
    words = text.split(" ")
    chunks: List[str] = []
    for i, word in enumerate(words):
        if i == 0:
            chunks.append(word)
        else:
            chunks.append(f" {word}")
    return chunks


class StreamingResponse(SimulatedResponse):
    """A streaming variant of :class:`SimulatedResponse`.

    Yields Server-Sent Events (SSE) strings from :meth:`iter_lines`.
    """

    def __init__(
        self,
        chunks: Optional[List[str]] = None,
        chunk_delay_ms: int = 30,
        response_id: Optional[str] = None,
        model: str = "chatassist-4",
    ):
        # Use default content when no chunks are supplied.
        if chunks is None:
            chunks = _split_into_word_chunks(_DEFAULT_STREAMING_TEXT)

        self._chunks = chunks
        self._chunk_delay_ms = chunk_delay_ms
        self._response_id = response_id or f"resp-{uuid.uuid4().hex[:12]}"
        self._model = model
        self._created = int(time.time())

        # Satisfy the base class — headers mimic a streaming 200 response.
        super().__init__(
            status_code=200,
            body={},
            headers={
                "Content-Type": "text/event-stream",
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Remaining": "59",
                "X-RateLimit-Reset": str(int(time.time()) + 60),
                "X-Request-Id": f"req-{uuid.uuid4().hex[:12]}",
            },
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def json(self):
        """Streaming responses do not support ``json()``."""
        raise RuntimeError("Use iter_lines() for streaming responses")

    def iter_lines(self):
        """Yield SSE-formatted lines with a configurable delay.

        Each yielded value is a ``str`` of the form::

            data: {"id":"resp-...","object":"chat.completion.chunk",...}

        The final content chunk carries ``finish_reason: "stop"`` and an
        accumulated ``usage`` block, followed by ``data: [DONE]``.
        """
        delay_s = self._chunk_delay_ms / 1000.0
        total_content = "".join(self._chunks)
        prompt_tokens = 42  # Deterministic placeholder
        completion_tokens = max(1, int(len(total_content.split()) * 1.3))

        for i, chunk_text in enumerate(self._chunks):
            is_last = i == len(self._chunks) - 1
            payload = {
                "id": self._response_id,
                "object": "chat.completion.chunk",
                "created": self._created,
                "model": self._model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk_text},
                        "finish_reason": "stop" if is_last else None,
                    }
                ],
            }
            if is_last:
                payload["usage"] = {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                }

            yield f"data: {json.dumps(payload)}"

            if not is_last and delay_s > 0:
                time.sleep(delay_s)

        yield "data: [DONE]"

    # ------------------------------------------------------------------ #
    # repr
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return (
            f"<StreamingResponse [{self.status_code}] "
            f"chunks={len(self._chunks)}>"
        )
