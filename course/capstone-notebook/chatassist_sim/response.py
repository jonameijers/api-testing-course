"""SimulatedResponse — mimics requests.Response for the ChatAssist simulator."""

import json
from typing import Any, Dict, Optional


class SimulatedResponse:
    """A lightweight stand-in for ``requests.Response``.

    Attributes:
        status_code: HTTP status code (e.g. 200, 401, 429).
        headers: Response headers including rate-limit info.
    """

    def __init__(
        self,
        status_code: int,
        body: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code: int = status_code
        self._body: Dict[str, Any] = body
        self.headers: Dict[str, str] = headers or {}

    # --------------------------------------------------------------------- #
    # Public helpers that mirror requests.Response
    # --------------------------------------------------------------------- #

    def json(self) -> Dict[str, Any]:
        """Return the response body as a Python dict."""
        return self._body

    @property
    def text(self) -> str:
        """Return the response body as a JSON string."""
        return json.dumps(self._body)

    def iter_lines(self):
        """Yield lines for streaming responses.

        The base class raises — ``StreamingResponse`` overrides this.
        """
        raise RuntimeError("Not a streaming response")

    # --------------------------------------------------------------------- #
    # Convenience dunder methods
    # --------------------------------------------------------------------- #

    def __repr__(self) -> str:
        return f"<SimulatedResponse [{self.status_code}]>"
