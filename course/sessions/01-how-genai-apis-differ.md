# Session 1: How GenAI APIs Differ from Normal APIs

**Duration:** 90 minutes
**Deliverable:** UI-to-API Bridge Reference (initial version)

## Learning Objectives

By the end of this session, you will be able to:

1. Explain why GenAI API responses are non-deterministic
2. Describe the role of temperature, top_p, and max_tokens
3. Distinguish between chat completion, structured output, tool calling, and streaming modes
4. Explain what tokens are and why token counts matter
5. Identify the key differences between testing a traditional REST API and a GenAI API

---

## Bridge from UI Testing (10 min)

In UI testing, you expect deterministic behavior. Click a button, see the same result. Fill in a form, get the same confirmation page. If a test passes once and fails the next time with no code change, that is a flaky test -- something is wrong.

GenAI APIs break this assumption on purpose.

| UI Testing | GenAI API Testing | What Changes |
|---|---|---|
| Deterministic page content | Non-deterministic text output | The same request can produce different responses, *by design* |
| Page load times vary | Response latency varies with output length | Timeouts need to be generous and dynamic |
| DOM elements have a fixed structure | GenAI responses are free-form text | You cannot rely on exact element matching |
| Visual regression compares screenshots | Semantic testing compares meaning | New assertion techniques are needed |
| Click button, same result | Send prompt, different result | The "contract" between client and server changes |

**Key insight:** The fundamental contract changes. Traditional APIs promise "same input, same output." GenAI APIs promise "same input, *reasonable* output." Your assertion strategy needs to match this new contract.

Even setting `temperature=0` does not guarantee identical outputs. Floating-point arithmetic and batch processing variations can produce subtly different results between calls. This is qualitatively different from UI flakiness caused by timing or animations -- it is built into how the model works.

---

## Section 1: Non-Determinism -- The Core Difference (15 min)

### Why Traditional APIs Are Deterministic

A traditional REST API runs fixed code paths. When you call `GET /users/42`, the server looks up user 42 in the database and returns their profile. Same query, same data, same response. The logic is a function: one input maps to one output.

### Why GenAI APIs Are Non-Deterministic

A GenAI API does not look up a stored answer. It *generates* one by predicting the next token (word fragment) based on probabilities. At each step, the model has multiple plausible next tokens, and it samples from this distribution. The result is that the same prompt can produce different completions.

Here is a concrete demonstration from the ChatAssist API. Sending the same request three times with `temperature: 1.5`:

**Request (sent 3 times):**
```json
{
  "model": "chatassist-4",
  "messages": [{"role": "user", "content": "Name a fruit."}],
  "temperature": 1.5,
  "max_tokens": 10
}
```

**Response 1:** `"Mango"`
**Response 2:** `"Starfruit"`
**Response 3:** `"Dragonfruit! It's a tropical favorite."`

All three are valid responses to "Name a fruit." None of them are bugs. But if your test asserts `response == "Mango"`, it will fail two out of three times. This is the core testing challenge: **you cannot assert on exact output text.**

### The Temperature Dial

Temperature controls how much randomness the model uses when selecting the next token:

| Temperature | Behavior | Testing Implication |
|-------------|----------|---------------------|
| `0.0` | Nearly deterministic -- picks the most probable token every time | Closest to traditional testing, but still not guaranteed identical |
| `0.3 - 0.7` | Balanced -- some variation, mostly reasonable | Common for production use, moderate assertion challenge |
| `1.0` | Default -- natural language variation | Standard testing difficulty |
| `1.5 - 2.0` | Highly creative -- picks less probable tokens | Hard to test, wide variation in outputs |

### top_p: An Alternative Control

`top_p` (nucleus sampling) is another way to control randomness. Instead of adjusting the probability distribution (temperature), it limits the *pool* of candidate tokens:

- `top_p: 1.0` -- consider all tokens (default)
- `top_p: 0.1` -- only consider tokens in the top 10% of probability mass

In practice, you typically adjust either temperature or top_p, not both. For testing purposes, the effect is similar: lower values mean more predictable output.

### What This Means for Test Design

The implication is stark: you need a different assertion strategy for GenAI APIs. Instead of checking *what* the response says word-for-word, you check *whether* it is reasonable. We will build this strategy in detail in Session 2 (The Assertion Ladder).

---

## Section 2: Tokens -- The Currency of GenAI (10 min)

### What Tokens Are

Tokens are subword units -- the building blocks a model uses to process text. A token is not the same as a word:

- Common words are often a single token: "hello" = 1 token
- Longer or uncommon words get split: "unbelievable" might be 3 tokens ("un", "believ", "able")
- A rough rule of thumb: 1 token is approximately 4 characters in English

### Why Token Counting Matters

Tokens are the unit of billing, context limits, and rate limits. Three things depend on them:

**1. Billing:** GenAI APIs charge per token. The ChatAssist API tracks this in every response:

```json
"usage": {
  "prompt_tokens": 42,
  "completion_tokens": 47,
  "total_tokens": 89
}
```

Your test suite consumes tokens. A large test suite running daily can accumulate significant costs if not managed carefully.

**2. Context window limits:** Each model has a maximum number of tokens it can process in a single request (prompt + response combined):

| Model | Context Window |
|-------|---------------|
| `chatassist-4` | 128,000 tokens |
| `chatassist-4-mini` | 32,000 tokens |
| `chatassist-3` | 8,000 tokens |

If your request exceeds the limit, you get a 400 error:

```json
{
  "error": {
    "type": "invalid_request",
    "message": "This request would require 135000 tokens, which exceeds the maximum context length of 128000 for model chatassist-4.",
    "code": 400
  }
}
```

**3. Rate limits:** As covered in Session 0, rate limits apply to both requests-per-minute *and* tokens-per-minute. A test suite can stay within the request limit but blow through the token limit.

### Hidden Costs to Watch For

Research has identified several hidden cost patterns that catch new testers off guard:

- **Reasoning tokens:** Some models consume internal reasoning tokens that appear on the bill but not in the response
- **Failed request tokens:** API calls that return errors still consume input tokens -- you pay to send the prompt even if the response fails
- **Agentic overhead:** Tool-calling workflows that make multiple round trips compound token costs at each step

Per-token prices have dropped dramatically (from $20 per million tokens in 2022 to roughly $0.40 per million in 2025), but consumption rates have exploded. Cost awareness needs to be built into test design from the start.

---

## Section 3: Four Modes of Operation (15 min)

The ChatAssist API supports four distinct modes. Each has different testing characteristics.

### Mode 1: Chat Completion

The most basic mode: send messages, receive text.

**Request:**
```json
{
  "model": "chatassist-4",
  "messages": [
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.0,
  "max_tokens": 50
}
```

**Response (simplified):**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "The capital of France is Paris."
    },
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18}
}
```

Chat completion supports multi-turn conversations by including previous messages in the `messages` array. The model sees the full conversation history and responds in context.

**Testing characteristics:** Output is free-form text. Non-deterministic. Assertion difficulty is highest here because you have no structural guarantees about the response format.

### Mode 2: Structured Output

Force the model to return valid JSON matching a schema you define. This is a game-changer for testability.

**Request (key addition -- `response_format`):**
```json
{
  "model": "chatassist-4",
  "messages": [
    {"role": "system", "content": "Classify the sentiment of customer reviews."},
    {"role": "user", "content": "Review: The product arrived quickly and works perfectly. Great value!"}
  ],
  "temperature": 0.0,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "sentiment_analysis",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral", "mixed"]},
          "confidence": {"type": "number"},
          "key_phrases": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["sentiment", "confidence", "key_phrases"],
        "additionalProperties": false
      }
    }
  }
}
```

**Response:**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "{\"sentiment\":\"positive\",\"confidence\":0.95,\"key_phrases\":[\"arrived quickly\",\"works perfectly\",\"great value\"]}"
    },
    "finish_reason": "stop"
  }]
}
```

Notice that the `content` field is still a JSON *string* -- your test code must parse it to validate the structure. With `strict: true`, the response achieves 100% schema conformance. This makes format-level assertions fully deterministic.

**Teaching this early matters:** Structured Outputs are your first line of defense for assertions. Whenever you can constrain the response format, you should. It converts a hard non-deterministic testing problem into a much easier one.

### Mode 3: Tool Calling

The model can request that your application execute external functions. This creates a multi-step conversation flow.

**Step 1 -- User asks a question:**
```json
{
  "model": "chatassist-4",
  "messages": [
    {"role": "user", "content": "Where is my order #12345?"}
  ],
  "tools": [{
    "type": "function",
    "function": {
      "name": "lookup_order",
      "description": "Look up the status and tracking info for a customer order",
      "parameters": {
        "type": "object",
        "properties": {
          "order_id": {"type": "string", "description": "The order number"}
        },
        "required": ["order_id"]
      }
    }
  }]
}
```

**Step 2 -- Model requests a tool call (instead of answering directly):**
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call-001",
        "type": "function",
        "function": {
          "name": "lookup_order",
          "arguments": "{\"order_id\": \"12345\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

**Step 3 -- You execute the tool and send results back:**
```json
{
  "messages": [
    ...previous messages...,
    {"role": "tool", "tool_call_id": "call-001", "content": "{\"status\": \"shipped\", \"tracking_number\": \"TRK-98765\"}"}
  ]
}
```

**Step 4 -- Model produces a final answer using the tool results:**
```json
{
  "choices": [{
    "message": {
      "content": "Your order #12345 has been shipped! Tracking number: TRK-98765."
    },
    "finish_reason": "stop"
  }]
}
```

**Key signals for testing:**
- `finish_reason: "tool_calls"` means the model wants to call a function, not answer directly
- `content: null` when a tool call is requested (no text response)
- `tool_choice` controls whether the model must, may, or must not call tools ("required", "auto", "none")

**Critical failure modes to test for:** Incorrect tool selection (model picks the wrong function), hallucinated parameter values (model makes up an order ID), and infinite loops (model keeps calling the same tool repeatedly). Component-level testing of individual tools should be deterministic -- the non-determinism comes from the model's *decision* to call them.

### Mode 4: Streaming

Receive the response incrementally via Server-Sent Events (SSE), instead of waiting for the full completion.

**Request:** Add `"stream": true` to any request.

**Response (stream of chunks):**
```
data: {"choices":[{"delta":{"role":"assistant","content":""},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":"An"},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":" API"},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":" is"},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":" like"},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":" a"},"finish_reason":null}]}
data: {"choices":[{"delta":{"content":" waiter"},"finish_reason":null}]}
...
data: {"choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":15,"completion_tokens":12,"total_tokens":27}}
data: [DONE]
```

Each chunk contains a `delta` with a small fragment of text. The final chunk has `finish_reason` and `usage`. The stream ends with `data: [DONE]`.

**Testing considerations:**
- You must concatenate all `delta.content` fragments to get the full response
- Mid-stream errors are possible -- the server can send an error event after partial content
- Time-to-first-token (100-500ms) is different from total completion time (can be seconds)
- The `usage` object only appears in the final chunk

---

## Section 4: Model Selection and Versioning (5 min)

The ChatAssist API offers multiple models:

| Model | Context Window | Use Case |
|-------|---------------|----------|
| `chatassist-4` | 128K tokens | Most capable, highest quality |
| `chatassist-4-mini` | 32K tokens | Faster, cheaper, good for high-volume testing |
| `chatassist-3` | 8K tokens | Legacy, still supported |

### Why Pinning Matters

The `model` field in the response may differ from what you requested. If you request `chatassist-4`, you might get back `chatassist-4-2024-08-06` -- the specific version that was served.

Model version drift is the number one operational surprise for new testers. Real-world examples from other providers illustrate this:

- A default model update changed output behavior silently, breaking tests for teams that did not pin to a specific version
- A model deprecated just months after release forced emergency migration
- Output structure regressions broke JSON parsing logic even when the API contract was unchanged

**The lesson:** Pin to a specific model version in your tests. Do not rely on aliases like "latest." Maintain a migration test suite for when you need to move to a new version. And budget for migration work as a regular cost, not a one-time event.

---

## Discussion and Q&A (15 min)

Consider these questions:

- Which of the four modes (completion, structured output, tool calling, streaming) would you encounter first in a real project? Why?
- How does non-determinism change your instinct about what a "passing test" means?
- What UI testing skills transfer directly to GenAI API testing? What needs to change?
- If you were testing a customer support chatbot built on ChatAssist, which mode would it likely use? What would make it hardest to test?

---

## Session Deliverable: UI-to-API Bridge Reference

This table maps UI testing concepts to their GenAI API equivalents. You will add to this reference in future sessions.

| UI Testing Concept | GenAI API Equivalent | What Changes |
|---|---|---|
| Deterministic page content | Non-deterministic text output | Assertion strategy must change -- cannot rely on exact text match |
| Page load timeout | Response latency (varies with output length) | Timeouts need to be generous and dynamic |
| DOM structure | JSON response structure | Structured output mode gives you predictable structure |
| Form validation errors | 400 Bad Request with error details | Error format is standardized in JSON |
| Login/authentication | API key in Authorization header | Simpler mechanism, but key security is critical |
| Visual regression (screenshot diff) | Semantic comparison (meaning diff) | New tools and techniques needed (covered in Session 2) |
| CSS selector for a specific element | JSON path for a specific field | `choices[0].message.content` instead of `#result .text` |
| Retrying due to network flakiness | Retrying due to rate limits or model variation | Need exponential backoff and smarter retry logic |
| Testing across browsers | Testing across model versions | Models drift over time; pin to specific versions |
| Page object pattern | Request builder pattern | Encapsulate request construction for reuse |
