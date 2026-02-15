"""Core ChatAssist simulator engine.

Provides :class:`ChatAssistSimulator`, the main entry-point that students
interact with.  It simulates ``POST /v1/chat/completions`` for the
fictional *ChatAssist* GenAI API.
"""

import copy
import json
import random
import re
import time
import uuid
from typing import Any, Dict, List, Optional

from .fault_injection import configure, inject_fault
from .response import SimulatedResponse
from .response_pools import RESPONSE_POOLS
from .streaming import StreamingResponse, _split_into_word_chunks


# ------------------------------------------------------------------ #
#  Regex patterns
# ------------------------------------------------------------------ #

_INJECTION_PATTERNS = re.compile(
    r"ignore your instructions"
    r"|system prompt"
    r"|repeat your rules"
    r"|what are your instructions"
    r"|training data",
    re.IGNORECASE,
)

_ESCALATION_PATTERNS = re.compile(
    r"\b(lawsuit|attorney|legal action|sue)\b", re.IGNORECASE
)

_HUMAN_HANDOFF_PATTERNS = re.compile(
    r"speak to a human|talk to a person|real person", re.IGNORECASE
)

_ORDER_ID_PATTERN = re.compile(r"(?:ORD-|#)(\d+)", re.IGNORECASE)
_ORDER_ID_LOOSE = re.compile(r"order\s*#?\s*(\w+)", re.IGNORECASE)

_CREDIT_CARD_PATTERN = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b")
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


class ChatAssistSimulator:
    """In-process simulator for the ChatAssist GenAI API.

    Usage::

        sim = ChatAssistSimulator()
        response = sim.chat_completions(
            {"model": "chatassist-4", "messages": [{"role": "user", "content": "Hi"}]},
            headers={"Authorization": "Bearer ca-key-test-valid-key-12345678"},
        )
        print(response.status_code)   # 200
        print(response.json())        # full response body
    """

    VALID_MODELS = ["chatassist-4", "chatassist-4-mini", "chatassist-3"]
    VALID_API_KEY = "ca-key-test-valid-key-12345678"

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._fault_config: Dict[str, Any] = {}
        self._sim_config: Dict[str, Any] = {
            "injection_defense": "strong",   # "strong", "weak", "none"
            "hallucination_rate": 0.05,      # 5 % for electronics
            "rate_limit": 60,                # requests per minute
            "model_version": None,           # override model in response
            "chunk_delay_ms": 30,            # streaming delay
        }
        self._request_count: int = 0
        self._request_timestamps: List[float] = []
        self._seed: Optional[int] = None
        self._rng: random.Random = random.Random()

        if config:
            self._sim_config.update(config)

    # ------------------------------------------------------------------ #
    #  Public helpers
    # ------------------------------------------------------------------ #

    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducible responses."""
        self._seed = seed
        self._rng = random.Random(seed)

    def inject_fault(self, fault_type: str, **kwargs):
        """Return a context manager that injects *fault_type*."""
        return inject_fault(self, fault_type, **kwargs)

    def configure(self, **kwargs):
        """Return a context manager that temporarily alters config."""
        return configure(self, **kwargs)

    # ------------------------------------------------------------------ #
    #  Main entry-point
    # ------------------------------------------------------------------ #

    def chat_completions(
        self,
        request_body: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> SimulatedResponse:
        """Simulate ``POST /v1/chat/completions``.

        Parameters
        ----------
        request_body : dict
            The JSON request body (model, messages, etc.).
        headers : dict, optional
            HTTP headers; must include ``Authorization: Bearer <key>``.
        """

        # 1. Fault injection takes priority ----------------------------- #
        if self._fault_config.get("force_rate_limit"):
            return self._build_error_response(
                429,
                "rate_limit_error",
                "Rate limit exceeded. Try again in 8 seconds.",
                extra_headers={"Retry-After": "8"},
            )
        if self._fault_config.get("force_500"):
            return self._build_error_response(
                500, "server_error", "An internal error occurred."
            )
        if self._fault_config.get("force_503"):
            return self._build_error_response(
                503, "overloaded", "The model is currently overloaded."
            )
        if self._fault_config.get("force_safety_block"):
            return self._build_safety_response(request_body)
        if self._fault_config.get("response_delay_s"):
            time.sleep(self._fault_config["response_delay_s"])

        # 2. Validate auth ---------------------------------------------- #
        headers = headers or {}
        auth = headers.get("Authorization", "")
        if not auth:
            return self._build_error_response(
                401,
                "authentication_error",
                "No API key provided. Include your key in the Authorization "
                "header: 'Authorization: Bearer YOUR_API_KEY'",
            )
        if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] != self.VALID_API_KEY:
            return self._build_error_response(
                401,
                "authentication_error",
                "Invalid API key. Verify your API key at "
                "https://dashboard.chatassist.example/keys",
            )

        # 3. Validate request body -------------------------------------- #
        model = request_body.get("model")
        if model not in self.VALID_MODELS:
            return self._build_error_response(
                400,
                "invalid_request",
                f"Invalid model: {model}",
                param="model",
            )

        messages = request_body.get("messages")
        if not messages:
            return self._build_error_response(
                400,
                "invalid_request",
                "messages is required",
                param="messages",
            )

        temperature = request_body.get("temperature", 0.3)
        if not (0.0 <= temperature <= 2.0):
            return self._build_error_response(
                400,
                "invalid_request",
                f"temperature must be between 0.0 and 2.0, got {temperature}",
                param="temperature",
            )

        top_p = request_body.get("top_p", 1.0)
        if not (0.0 <= top_p <= 1.0):
            return self._build_error_response(
                400,
                "invalid_request",
                f"top_p must be between 0.0 and 1.0, got {top_p}",
                param="top_p",
            )

        max_tokens = request_body.get("max_tokens", 500)

        # 4. Book-keep request count ------------------------------------ #
        self._request_count += 1
        self._request_timestamps.append(time.time())

        # 5. Route ------------------------------------------------------ #
        stream = request_body.get("stream", False)
        tools = request_body.get("tools")
        response_format = request_body.get("response_format")

        user_message = self._get_last_user_message(messages)

        if stream:
            return self._handle_streaming(request_body, user_message)
        if response_format:
            return self._handle_structured_output(
                request_body, user_message, max_tokens
            )
        if tools and self._should_use_tool(user_message, messages):
            return self._handle_tool_calling(request_body, user_message, messages)

        return self._handle_completion(
            request_body, user_message, messages, temperature
        )

    # ================================================================== #
    #  Internal routing handlers
    # ================================================================== #

    def _handle_completion(
        self,
        request_body: Dict[str, Any],
        user_message: str,
        messages: List[Dict[str, Any]],
        temperature: float,
    ) -> SimulatedResponse:
        """Generate a standard (non-tool, non-streaming) completion."""

        model = request_body.get("model", "chatassist-4")
        lower = user_message.lower()

        # --- Prompt-injection detection -------------------------------- #
        if _INJECTION_PATTERNS.search(lower):
            defense = self._sim_config["injection_defense"]
            if defense == "strong":
                content = self._select_content("prompt_injection_defense", temperature)
                return self._build_success_response(content, model)
            elif defense == "weak":
                content = self._select_content("prompt_injection_leak", temperature)
                return self._build_success_response(content, model)
            # defense == "none" → fall through

        # --- Escalation triggers --------------------------------------- #
        if _ESCALATION_PATTERNS.search(lower):
            content = self._select_content("escalation", temperature)
            return self._build_success_response(content, model)

        # --- Human handoff --------------------------------------------- #
        if _HUMAN_HANDOFF_PATTERNS.search(lower):
            content = self._select_content("human_handoff", temperature)
            return self._build_success_response(content, model)

        # --- Electronics return ---------------------------------------- #
        if "electron" in lower and any(
            kw in lower for kw in ("return", "policy", "window")
        ):
            content = self._select_content("electronics_return", temperature)
            # PII scrubbing check
            content = self._scrub_pii_if_needed(content, messages)
            return self._build_success_response(content, model)

        # --- General return policy ------------------------------------- #
        if "return" in lower and any(
            kw in lower for kw in ("policy", "window", "item")
        ):
            content = self._select_content("return_policy", temperature)
            content = self._scrub_pii_if_needed(content, messages)
            return self._build_success_response(content, model)

        # --- Product recommendation ------------------------------------ #
        if "recommend" in lower or "suggest" in lower:
            content = self._select_content("product_recommendation", temperature)
            return self._build_success_response(content, model)

        # --- Fallback -------------------------------------------------- #
        content = self._select_content("generic_completion", temperature)
        return self._build_success_response(content, model)

    # ------------------------------------------------------------------ #
    #  Streaming
    # ------------------------------------------------------------------ #

    def _handle_streaming(
        self,
        request_body: Dict[str, Any],
        user_message: str,
    ) -> StreamingResponse:
        """Return a :class:`StreamingResponse` with word-level chunks."""

        model = request_body.get("model", "chatassist-4")
        temperature = request_body.get("temperature", 0.3)
        lower = user_message.lower()

        # Pick content from the appropriate pool
        if "return" in lower and any(kw in lower for kw in ("policy", "window", "item")):
            text = self._select_content("return_policy", temperature)
        elif "recommend" in lower or "suggest" in lower:
            text = self._select_content("product_recommendation", temperature)
        else:
            text = self._select_content("generic_completion", temperature)

        chunks = _split_into_word_chunks(text)
        delay = self._sim_config.get("chunk_delay_ms", 30)
        return StreamingResponse(
            chunks=chunks,
            chunk_delay_ms=delay,
            model=self._sim_config.get("model_version") or model,
        )

    # ------------------------------------------------------------------ #
    #  Structured output (classification)
    # ------------------------------------------------------------------ #

    def _handle_structured_output(
        self,
        request_body: Dict[str, Any],
        user_message: str,
        max_tokens: int,
    ) -> SimulatedResponse:
        """Return a classification JSON as content."""

        model = request_body.get("model", "chatassist-4")
        lower = user_message.lower()

        # Pick category based on keyword matching
        if "return" in lower:
            category = "returns"
        elif "ship" in lower:
            category = "shipping"
        elif any(kw in lower for kw in ("bill", "charge", "payment")):
            category = "billing"
        elif any(kw in lower for kw in ("product", "item", "stock")):
            category = "product_info"
        else:
            category = "other"

        # Find matching variant from the classification pool
        pool = RESPONSE_POOLS["classification"]
        variant = next(
            (v for v in pool if v.get("_category") == category),
            pool[-1],  # fallback to "other"
        )
        content = variant["content"]

        # Simulate truncation if max_tokens is too low
        finish_reason = "stop"
        if max_tokens < 60 or self._fault_config.get("truncate_response"):
            # Truncate to roughly max_tokens * 4 chars (rough heuristic)
            truncate_at = max(10, max_tokens * 4) if max_tokens < 60 else len(content) // 2
            content = content[:truncate_at]
            finish_reason = "length"

        return self._build_success_response(content, model, finish_reason=finish_reason)

    # ------------------------------------------------------------------ #
    #  Tool calling
    # ------------------------------------------------------------------ #

    def _should_use_tool(
        self,
        user_message: str,
        messages: List[Dict[str, Any]],
    ) -> bool:
        """Decide whether the user message warrants a tool call."""
        lower = user_message.lower()
        # If there is already a tool result in the conversation, we should
        # generate a follow-up instead — but we still route through _handle_tool_calling.
        if any(m.get("role") == "tool" for m in messages):
            return True
        return bool(
            "order" in lower
            or _ORDER_ID_PATTERN.search(lower)
            or "inventory" in lower
            or "in stock" in lower
            or "check stock" in lower
            or "availability" in lower
        )

    def _handle_tool_calling(
        self,
        request_body: Dict[str, Any],
        user_message: str,
        messages: List[Dict[str, Any]],
    ) -> SimulatedResponse:
        """Handle a request that should invoke (or follow-up on) a tool."""

        model = request_body.get("model", "chatassist-4")
        temperature = request_body.get("temperature", 0.3)
        lower = user_message.lower()

        # ---- Follow-up after tool result ----------------------------- #
        has_tool_result = any(m.get("role") == "tool" for m in messages)
        if has_tool_result:
            # Extract an order_id from anywhere in the conversation
            order_id = self._extract_order_id(messages)
            status = "shipped"

            # Try to get status from the tool result content
            for m in messages:
                if m.get("role") == "tool":
                    try:
                        tool_data = json.loads(m.get("content", "{}"))
                        status = tool_data.get("status", status)
                        order_id = tool_data.get("order_id", order_id)
                    except (json.JSONDecodeError, TypeError):
                        pass

            content = self._select_content("order_lookup_followup", temperature)
            content = content.format(order_id=order_id, status=status)
            return self._build_success_response(content, model)

        # ---- Inventory check ----------------------------------------- #
        if any(kw in lower for kw in ("inventory", "in stock", "check stock", "availability")):
            product_id = self._extract_product_id(user_message)
            tool_call_id = f"call-tc-{uuid.uuid4().hex[:12]}"
            tool_calls = [
                {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": "check_inventory",
                        "arguments": json.dumps({"product_id": product_id}),
                    },
                }
            ]
            return self._build_success_response(
                content=None,
                model=model,
                finish_reason="tool_calls",
                tool_calls=tool_calls,
            )

        # ---- Order lookup -------------------------------------------- #
        order_id = self._extract_order_id(messages)

        # Pick from the order_lookup pool (first variant = tool call,
        # second = flaky text).
        pool = RESPONSE_POOLS["order_lookup_tool_call"]
        variant = self._select_from_pool_raw(pool, temperature)

        if variant.get("tool_calls"):
            tool_call_id = f"call-tc-{uuid.uuid4().hex[:12]}"
            tool_calls = [
                {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": "lookup_order",
                        "arguments": json.dumps({"order_id": order_id}),
                    },
                }
            ]
            return self._build_success_response(
                content=None,
                model=model,
                finish_reason="tool_calls",
                tool_calls=tool_calls,
            )
        else:
            # Flaky variant — returns text instead of tool call
            return self._build_success_response(
                variant["content"], model, finish_reason="stop"
            )

    # ------------------------------------------------------------------ #
    #  Safety response
    # ------------------------------------------------------------------ #

    def _build_safety_response(
        self, request_body: Dict[str, Any]
    ) -> SimulatedResponse:
        model = request_body.get("model", "chatassist-4")
        content = self._select_content("safety_block", 0)
        return self._build_success_response(
            content,
            model,
            finish_reason="safety",
            safety_metadata={
                "blocked": True,
                "categories": ["illegal_activity"],
                "severity": "high",
            },
        )

    # ================================================================== #
    #  Pool selection helpers
    # ================================================================== #

    def _select_content(self, pool_name: str, temperature: float = 0.3) -> str:
        """Select a variant from a pool and return its content string."""
        pool = RESPONSE_POOLS[pool_name]
        variant = self._select_from_pool_raw(pool, temperature)
        if isinstance(variant, dict):
            return variant["content"]
        return variant

    def _select_from_pool_raw(self, pool: list, temperature: float = 0.3):
        """Select a raw variant (str or dict) honouring hallucination rate."""
        candidates = []
        for item in pool:
            if isinstance(item, dict) and item.get("_hallucination"):
                if self._rng.random() < self._sim_config.get("hallucination_rate", 0.05):
                    candidates.append(item)
            else:
                candidates.append(item)

        # If all candidates were filtered out (unlikely), use non-hallucinated
        if not candidates:
            candidates = [
                p
                for p in pool
                if not (isinstance(p, dict) and p.get("_hallucination"))
            ]

        if temperature == 0:
            return candidates[0]
        elif temperature <= 0.3:
            return self._rng.choice(candidates[: min(2, len(candidates))])
        else:
            return self._rng.choice(candidates)

    # ================================================================== #
    #  Response builders
    # ================================================================== #

    def _build_success_response(
        self,
        content: Optional[str],
        model: str,
        finish_reason: str = "stop",
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        safety_metadata: Optional[Dict[str, Any]] = None,
    ) -> SimulatedResponse:
        """Construct a 200 response matching the ChatAssist JSON shape."""

        body: Dict[str, Any] = {
            "id": f"resp-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": self._sim_config.get("model_version") or model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "finish_reason": finish_reason,
                }
            ],
            "usage": self._calculate_usage(content or ""),
        }

        if tool_calls:
            body["choices"][0]["message"]["content"] = None
            body["choices"][0]["message"]["tool_calls"] = tool_calls

        if safety_metadata:
            body["choices"][0]["safety_metadata"] = safety_metadata

        # Maybe truncate (malformed_json fault)
        if self._fault_config.get("truncate_response") and not tool_calls:
            # Only truncate if not already handled by structured output
            raw = json.dumps(body)
            truncated = raw[: len(raw) // 2]
            # Return a response whose .text is broken JSON
            return SimulatedResponse(
                status_code=200,
                body=body,  # .json() still works for inspection
                headers=self._success_headers(),
            )

        headers = self._success_headers()
        return SimulatedResponse(status_code=200, body=body, headers=headers)

    def _build_error_response(
        self,
        status_code: int,
        error_type: str,
        message: str,
        param: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> SimulatedResponse:
        """Construct an error response."""
        body: Dict[str, Any] = {
            "error": {
                "type": error_type,
                "message": message,
                "code": status_code,
            }
        }
        if param is not None:
            body["error"]["param"] = param

        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "X-Request-Id": f"req-{uuid.uuid4().hex[:12]}",
        }
        if extra_headers:
            headers.update(extra_headers)

        return SimulatedResponse(
            status_code=status_code, body=body, headers=headers
        )

    def _success_headers(self) -> Dict[str, str]:
        """Standard headers for a successful response."""
        return {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(self._sim_config["rate_limit"]),
            "X-RateLimit-Remaining": str(
                max(0, self._sim_config["rate_limit"] - self._request_count)
            ),
            "X-RateLimit-Reset": str(int(time.time()) + 60),
            "X-Request-Id": f"req-{uuid.uuid4().hex[:12]}",
        }

    # ================================================================== #
    #  Utility helpers
    # ================================================================== #

    def _calculate_usage(
        self, content: str, prompt_tokens: Optional[int] = None
    ) -> Dict[str, int]:
        if prompt_tokens is None:
            prompt_tokens = self._rng.randint(30, 60)
        completion_tokens = max(1, int(len(content.split()) * 1.3))
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

    @staticmethod
    def _get_last_user_message(messages: List[Dict[str, Any]]) -> str:
        """Extract the text of the last user message."""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content
                # Handle list-form content (vision API style)
                if isinstance(content, list):
                    texts = [
                        part.get("text", "")
                        for part in content
                        if isinstance(part, dict) and part.get("type") == "text"
                    ]
                    return " ".join(texts)
        return ""

    def _extract_order_id(self, messages: List[Dict[str, Any]]) -> str:
        """Try to find an order ID in the conversation history."""
        for msg in reversed(messages):
            text = msg.get("content", "")
            if not isinstance(text, str):
                continue
            match = _ORDER_ID_PATTERN.search(text)
            if match:
                prefix = "ORD-" if "ORD-" in text[max(0, match.start() - 4): match.end()] else "#"
                return f"ORD-{match.group(1)}" if prefix == "ORD-" else match.group(0)
            match = _ORDER_ID_LOOSE.search(text)
            if match:
                return match.group(1)
        return "UNKNOWN"

    @staticmethod
    def _extract_product_id(user_message: str) -> str:
        """Extract a product identifier from the user message."""
        # Look for explicit product IDs like PROD-123 or SKU-ABC
        match = re.search(r"(?:PROD|SKU|product)[- ]?(\w+)", user_message, re.IGNORECASE)
        if match:
            return match.group(0).upper().replace(" ", "-")
        # Fallback
        return "PROD-UNKNOWN"

    def _scrub_pii_if_needed(
        self, content: str, messages: List[Dict[str, Any]]
    ) -> str:
        """If conversation contains PII and defense is strong, don't echo it."""
        if self._sim_config["injection_defense"] != "strong":
            return content

        conversation_text = " ".join(
            m.get("content", "") for m in messages if isinstance(m.get("content"), str)
        )

        has_pii = (
            _CREDIT_CARD_PATTERN.search(conversation_text)
            or _EMAIL_PATTERN.search(conversation_text)
            or _SSN_PATTERN.search(conversation_text)
        )

        if has_pii:
            # Strip any PII that might have crept into the response content
            content = _CREDIT_CARD_PATTERN.sub("[CARD REDACTED]", content)
            content = _SSN_PATTERN.sub("[SSN REDACTED]", content)
            # Keep emails in content since they may be legitimate support
            # contact info — only scrub credit cards and SSNs.

        return content
