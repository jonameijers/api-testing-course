# ChatAssist API Specification

> **Fictional API for educational purposes.** ChatAssist is a vendor-neutral GenAI API designed to illustrate testing concepts. It intentionally resembles real-world GenAI APIs without copying any specific vendor.

## Overview

ChatAssist is a conversational AI service that generates text responses from input messages. It supports four modes of operation:

| Mode | Description |
|------|-------------|
| **Chat Completion** | Send messages, receive a complete text response |
| **Structured Output** | Enforce a JSON schema on the response |
| **Tool Calling** | The model can request execution of external functions |
| **Streaming** | Receive the response incrementally via Server-Sent Events |

**Base URL:** `https://api.chatassist.example/v1`

---

## Authentication

All requests require an API key passed in the `Authorization` header:

```
Authorization: Bearer ca-key-abc123def456
```

API keys follow the format `ca-key-{32 alphanumeric characters}`.

### Rate Limiting

| Tier | Requests/min | Tokens/min | Tokens/day |
|------|-------------|------------|------------|
| Free | 10 | 10,000 | 100,000 |
| Standard | 60 | 100,000 | 2,000,000 |
| Enterprise | 300 | 1,000,000 | unlimited |

Rate limit status is returned in response headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1700000060
X-TokenLimit-Remaining: 95420
```

When rate limited, the API returns `429 Too Many Requests` with a `Retry-After` header (in seconds).

---

## Models

| Model ID | Context Window | Description |
|----------|---------------|-------------|
| `chatassist-4` | 128,000 tokens | Latest, most capable model |
| `chatassist-4-mini` | 32,000 tokens | Faster, cheaper, slightly less capable |
| `chatassist-3` | 8,000 tokens | Legacy model, still supported |

---

## Endpoint: Chat Completion

### `POST /v1/chat/completions`

Generate a text response from a conversation.

### Request Body

```json
{
  "model": "chatassist-4",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful customer support agent for an e-commerce store."
    },
    {
      "role": "user",
      "content": "What is your return policy?"
    }
  ],
  "temperature": 0.7,
  "top_p": 1.0,
  "max_tokens": 500,
  "stop": ["\n\n"],
  "safety": {
    "level": "standard"
  }
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | yes | — | Model ID to use |
| `messages` | array | yes | — | Conversation history (see Message Format below) |
| `temperature` | float | no | 1.0 | Randomness control. Range: 0.0 to 2.0. Lower = more deterministic |
| `top_p` | float | no | 1.0 | Nucleus sampling. Range: 0.0 to 1.0. Alternative to temperature |
| `max_tokens` | integer | no | model default | Maximum tokens in the response |
| `stop` | string or array | no | null | Stop sequence(s) — generation halts when encountered |
| `safety` | object | no | `{"level": "standard"}` | Safety/moderation settings (see Safety section) |
| `stream` | boolean | no | false | Enable streaming mode (see Streaming section) |
| `response_format` | object | no | null | Enforce structured output (see Structured Output section) |
| `tools` | array | no | null | Available tools/functions (see Tool Calling section) |
| `tool_choice` | string or object | no | `"auto"` | Control tool selection behavior |

### Message Format

Each message in the `messages` array has:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | yes | One of: `system`, `user`, `assistant`, `tool` |
| `content` | string | yes* | The message text (*may be null for assistant messages with tool calls) |
| `tool_calls` | array | no | Tool invocations made by the assistant |
| `tool_call_id` | string | no | ID linking a tool result to the original call |

### Response

```json
{
  "id": "resp-abc123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Our return policy allows returns within 30 days of purchase. Items must be in original condition with tags attached. To start a return, visit your order history page and select the item you'd like to return."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 47,
    "total_tokens": 89
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique response identifier |
| `object` | string | Always `"chat.completion"` |
| `created` | integer | Unix timestamp |
| `model` | string | Model used (may differ from requested if aliased) |
| `choices` | array | Array of completions (typically 1) |
| `choices[].index` | integer | Index of the choice |
| `choices[].message` | object | The assistant's response message |
| `choices[].finish_reason` | string | Why generation stopped: `stop`, `length`, `tool_calls`, `safety` |
| `usage` | object | Token consumption for this request |

### Finish Reasons

| Value | Meaning |
|-------|---------|
| `stop` | Natural end of response or hit a stop sequence |
| `length` | Hit `max_tokens` limit (response may be truncated) |
| `tool_calls` | Model wants to call one or more tools |
| `safety` | Response blocked by safety filter |

---

## Structured Output Mode

Force the model to return valid JSON conforming to a provided JSON Schema.

### Request

Add `response_format` to the request body:

```json
{
  "model": "chatassist-4",
  "messages": [
    {
      "role": "system",
      "content": "Extract product information from the user's message."
    },
    {
      "role": "user",
      "content": "I bought the UltraWidget Pro for $49.99 last Tuesday and it arrived broken."
    }
  ],
  "temperature": 0.0,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "product_extraction",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "product_name": { "type": "string" },
          "price": { "type": "number" },
          "issue": { "type": "string", "enum": ["broken", "wrong_item", "missing", "other"] },
          "purchase_date_mentioned": { "type": "boolean" }
        },
        "required": ["product_name", "price", "issue", "purchase_date_mentioned"],
        "additionalProperties": false
      }
    }
  }
}
```

### Response

```json
{
  "id": "resp-def456",
  "object": "chat.completion",
  "created": 1700000100,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"product_name\":\"UltraWidget Pro\",\"price\":49.99,\"issue\":\"broken\",\"purchase_date_mentioned\":true}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 95,
    "completion_tokens": 28,
    "total_tokens": 123
  }
}
```

**Note:** The `content` field is always a JSON string. Your test code must parse it to validate structure.

### Structured Output Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `response_format.type` | string | Must be `"json_schema"` |
| `response_format.json_schema.name` | string | A label for this schema |
| `response_format.json_schema.strict` | boolean | When `true`, response must match exactly. When `false`, best-effort |
| `response_format.json_schema.schema` | object | A valid JSON Schema (draft 2020-12 subset) |

### Strict Mode Limitations

When `strict: true`:
- All `properties` must appear in `required`
- `additionalProperties` must be `false`
- Supported types: `string`, `number`, `integer`, `boolean`, `array`, `object`, `null`
- `enum` is supported for strings
- Nested objects and arrays of objects are supported
- Max nesting depth: 5 levels
- Max total properties: 100

---

## Tool Calling (Function Calling)

The model can request that your application execute external functions, then continue the conversation with the results.

### Request (Define Available Tools)

```json
{
  "model": "chatassist-4",
  "messages": [
    {
      "role": "system",
      "content": "You are a customer support agent. Use the available tools to look up order information."
    },
    {
      "role": "user",
      "content": "Where is my order #12345?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "lookup_order",
        "description": "Look up the status and tracking info for a customer order",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": {
              "type": "string",
              "description": "The order number, e.g. '12345'"
            }
          },
          "required": ["order_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "check_inventory",
        "description": "Check current inventory for a product",
        "parameters": {
          "type": "object",
          "properties": {
            "product_id": {
              "type": "string",
              "description": "The product SKU"
            }
          },
          "required": ["product_id"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

### Response (Model Requests Tool Call)

```json
{
  "id": "resp-ghi789",
  "object": "chat.completion",
  "created": 1700000200,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call-001",
            "type": "function",
            "function": {
              "name": "lookup_order",
              "arguments": "{\"order_id\": \"12345\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 128,
    "completion_tokens": 22,
    "total_tokens": 150
  }
}
```

### Follow-Up Request (Provide Tool Results)

```json
{
  "model": "chatassist-4",
  "messages": [
    {
      "role": "system",
      "content": "You are a customer support agent. Use the available tools to look up order information."
    },
    {
      "role": "user",
      "content": "Where is my order #12345?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call-001",
          "type": "function",
          "function": {
            "name": "lookup_order",
            "arguments": "{\"order_id\": \"12345\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call-001",
      "content": "{\"status\": \"shipped\", \"tracking_number\": \"TRK-98765\", \"carrier\": \"FastShip\", \"estimated_delivery\": \"2024-11-20\"}"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "lookup_order",
        "description": "Look up the status and tracking info for a customer order",
        "parameters": {
          "type": "object",
          "properties": {
            "order_id": { "type": "string", "description": "The order number" }
          },
          "required": ["order_id"]
        }
      }
    }
  ]
}
```

### Response (Final Answer Using Tool Results)

```json
{
  "id": "resp-jkl012",
  "object": "chat.completion",
  "created": 1700000300,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Your order #12345 has been shipped! It's being delivered by FastShip with tracking number TRK-98765. The estimated delivery date is November 20, 2024."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 195,
    "completion_tokens": 41,
    "total_tokens": 236
  }
}
```

### Tool Choice Options

| Value | Behavior |
|-------|----------|
| `"auto"` | Model decides whether to call a tool |
| `"none"` | Model must not call any tool |
| `"required"` | Model must call at least one tool |
| `{"type": "function", "function": {"name": "lookup_order"}}` | Model must call the specified tool |

---

## Streaming Mode

Receive the response incrementally via Server-Sent Events (SSE).

### Request

Set `"stream": true` in the request body:

```json
{
  "model": "chatassist-4",
  "messages": [
    {
      "role": "user",
      "content": "Explain what an API is in simple terms."
    }
  ],
  "stream": true,
  "max_tokens": 200
}
```

### Response (SSE Stream)

The response is a series of `text/event-stream` events:

```
data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":"An"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" API"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" is"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" like"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" a"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" waiter"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" in"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" a"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":" restaurant"},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":"."},"finish_reason":null}]}

data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":15,"completion_tokens":12,"total_tokens":27}}

data: [DONE]
```

### Streaming Behavior

- Each chunk contains a `delta` object with incremental content
- The first chunk includes `delta.role` to establish the assistant role
- Subsequent chunks include `delta.content` with text fragments
- The final content chunk has an empty `delta` and a `finish_reason`
- `usage` is included only in the final chunk
- The stream ends with `data: [DONE]`
- If streaming a tool call, `delta` contains `tool_calls` array fragments instead of `content`

### Streaming Error Mid-Stream

If an error occurs mid-stream, the server sends an error event:

```
data: {"id":"resp-mno345","object":"chat.completion.chunk","created":1700000400,"model":"chatassist-4","choices":[{"index":0,"delta":{"content":"An API"},"finish_reason":null}]}

data: {"error":{"type":"server_error","message":"Internal processing error","code":500}}

data: [DONE]
```

---

## Safety and Moderation

### Safety Levels

Configure content moderation via the `safety` parameter:

| Level | Behavior |
|-------|----------|
| `"strict"` | Aggressive filtering. Blocks borderline content. Higher false-positive rate |
| `"standard"` | Balanced filtering. Default for most use cases |
| `"minimal"` | Permissive filtering. Only blocks clearly harmful content |

### Request

```json
{
  "model": "chatassist-4",
  "messages": [
    {
      "role": "user",
      "content": "How do I pick a lock?"
    }
  ],
  "safety": {
    "level": "strict",
    "categories": ["violence", "illegal_activity", "adult_content", "pii_exposure"]
  }
}
```

### Safety Block Response

When content is blocked, the response has `finish_reason: "safety"`:

```json
{
  "id": "resp-pqr678",
  "object": "chat.completion",
  "created": 1700000500,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I'm unable to provide instructions on that topic."
      },
      "finish_reason": "safety",
      "safety_metadata": {
        "blocked": true,
        "categories": ["illegal_activity"],
        "severity": "high"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 10,
    "total_tokens": 22
  }
}
```

### Safety Categories

| Category | Description |
|----------|-------------|
| `violence` | Content promoting or describing violence |
| `illegal_activity` | Instructions for illegal actions |
| `adult_content` | Sexually explicit material |
| `pii_exposure` | Personally identifiable information in the output |
| `self_harm` | Content related to self-harm |
| `hate_speech` | Discriminatory or hateful language |

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "type": "error_type",
    "message": "Human-readable description",
    "code": 400,
    "param": "field_name"
  }
}
```

### Error Catalog

#### 400 Bad Request — Malformed JSON

```json
{
  "error": {
    "type": "invalid_request",
    "message": "Request body must be valid JSON. Unexpected token '}' at position 42.",
    "code": 400
  }
}
```

#### 400 Bad Request — Invalid Parameter

```json
{
  "error": {
    "type": "invalid_request",
    "message": "temperature must be between 0.0 and 2.0, got 3.5",
    "code": 400,
    "param": "temperature"
  }
}
```

#### 400 Bad Request — Context Window Exceeded

```json
{
  "error": {
    "type": "invalid_request",
    "message": "This request would require 135000 tokens, which exceeds the maximum context length of 128000 for model chatassist-4.",
    "code": 400,
    "param": "messages"
  }
}
```

#### 400 Bad Request — Invalid JSON Schema (Structured Output)

```json
{
  "error": {
    "type": "invalid_request",
    "message": "Invalid JSON Schema in response_format: 'additionalProperties' must be false when strict mode is enabled.",
    "code": 400,
    "param": "response_format.json_schema.schema"
  }
}
```

#### 401 Unauthorized — Missing or Invalid API Key

```json
{
  "error": {
    "type": "authentication_error",
    "message": "Invalid API key. Verify your API key at https://dashboard.chatassist.example/keys",
    "code": 401
  }
}
```

#### 403 Forbidden — Model Access Denied

```json
{
  "error": {
    "type": "permission_error",
    "message": "Your API key does not have access to model 'chatassist-4'. Upgrade your plan at https://dashboard.chatassist.example/billing",
    "code": 403,
    "param": "model"
  }
}
```

#### 429 Too Many Requests — Rate Limited

```json
{
  "error": {
    "type": "rate_limit_error",
    "message": "Rate limit exceeded. Try again in 12 seconds.",
    "code": 429
  }
}
```

Response headers:
```
Retry-After: 12
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000072
```

#### 429 Too Many Requests — Token Quota Exceeded

```json
{
  "error": {
    "type": "quota_exceeded",
    "message": "Daily token quota exceeded. Resets at midnight UTC. Current usage: 2,000,000 / 2,000,000 tokens.",
    "code": 429
  }
}
```

#### 500 Internal Server Error

```json
{
  "error": {
    "type": "server_error",
    "message": "An internal error occurred. Please retry your request. If the problem persists, contact support@chatassist.example",
    "code": 500
  }
}
```

#### 503 Service Unavailable — Model Overloaded

```json
{
  "error": {
    "type": "overloaded",
    "message": "The model is currently overloaded. Please retry after a brief wait.",
    "code": 503
  }
}
```

---

## Complete Request/Response Examples

### Example 1: Simple Chat Completion

**Request:**
```bash
curl -X POST https://api.chatassist.example/v1/chat/completions \
  -H "Authorization: Bearer ca-key-abc123def456" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatassist-4",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "temperature": 0.0,
    "max_tokens": 50
  }'
```

**Response:**
```json
{
  "id": "resp-ex1-001",
  "object": "chat.completion",
  "created": 1700001000,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 11,
    "completion_tokens": 7,
    "total_tokens": 18
  }
}
```

### Example 2: Multi-Turn Conversation

**Request:**
```bash
curl -X POST https://api.chatassist.example/v1/chat/completions \
  -H "Authorization: Bearer ca-key-abc123def456" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatassist-4",
    "messages": [
      {"role": "system", "content": "You are a math tutor. Show your work step by step."},
      {"role": "user", "content": "What is 15% of 240?"},
      {"role": "assistant", "content": "To find 15% of 240:\n\nStep 1: Convert 15% to decimal: 15/100 = 0.15\nStep 2: Multiply: 0.15 x 240 = 36\n\nSo 15% of 240 is 36."},
      {"role": "user", "content": "Now what is 20% of the same number?"}
    ],
    "temperature": 0.3,
    "max_tokens": 150
  }'
```

**Response:**
```json
{
  "id": "resp-ex2-001",
  "object": "chat.completion",
  "created": 1700001100,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "To find 20% of 240:\n\nStep 1: Convert 20% to decimal: 20/100 = 0.20\nStep 2: Multiply: 0.20 x 240 = 48\n\nSo 20% of 240 is 48."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 98,
    "completion_tokens": 52,
    "total_tokens": 150
  }
}
```

### Example 3: Structured Output with Validation

**Request:**
```bash
curl -X POST https://api.chatassist.example/v1/chat/completions \
  -H "Authorization: Bearer ca-key-abc123def456" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatassist-4",
    "messages": [
      {"role": "system", "content": "Classify the sentiment of customer reviews."},
      {"role": "user", "content": "Review: The product arrived quickly and works perfectly. Great value for money!"}
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
  }'
```

**Response:**
```json
{
  "id": "resp-ex3-001",
  "object": "chat.completion",
  "created": 1700001200,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"sentiment\":\"positive\",\"confidence\":0.95,\"key_phrases\":[\"arrived quickly\",\"works perfectly\",\"great value\"]}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 112,
    "completion_tokens": 32,
    "total_tokens": 144
  }
}
```

### Example 4: Tool Calling — Weather Lookup

**Request:**
```bash
curl -X POST https://api.chatassist.example/v1/chat/completions \
  -H "Authorization: Bearer ca-key-abc123def456" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatassist-4",
    "messages": [
      {"role": "user", "content": "What should I wear in Amsterdam today?"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "description": "Get current weather for a city",
          "parameters": {
            "type": "object",
            "properties": {
              "city": {"type": "string"},
              "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
          }
        }
      }
    ]
  }'
```

**Response (tool call requested):**
```json
{
  "id": "resp-ex4-001",
  "object": "chat.completion",
  "created": 1700001300,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call-wx-001",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"city\": \"Amsterdam\", \"units\": \"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 72,
    "completion_tokens": 25,
    "total_tokens": 97
  }
}
```

### Example 5: Temperature Effects on Non-Determinism

Sending the same request three times with `temperature: 1.5`:

**Request (sent 3 times):**
```json
{
  "model": "chatassist-4",
  "messages": [{"role": "user", "content": "Name a fruit."}],
  "temperature": 1.5,
  "max_tokens": 10
}
```

**Response 1:**
```json
{"choices": [{"message": {"content": "Mango"}, "finish_reason": "stop"}]}
```

**Response 2:**
```json
{"choices": [{"message": {"content": "Starfruit"}, "finish_reason": "stop"}]}
```

**Response 3:**
```json
{"choices": [{"message": {"content": "Dragonfruit! It's a tropical favorite."}, "finish_reason": "stop"}]}
```

This illustrates the core testing challenge: **the same input produces different outputs**.

---

## Response Latency Characteristics

Typical response times (for testing timeout and performance expectations):

| Scenario | Typical Latency |
|----------|----------------|
| Short completion (< 50 tokens) | 200 - 800 ms |
| Medium completion (50-200 tokens) | 800 ms - 3 s |
| Long completion (200-1000 tokens) | 3 - 15 s |
| Structured output | +10-20% vs. equivalent plain text |
| Tool calling (model decision) | 300 ms - 2 s |
| Streaming (time to first token) | 100 - 500 ms |
| Streaming (inter-token interval) | 20 - 80 ms |

**Note:** These are approximate. Real latency varies with model load, prompt complexity, and network conditions. Tests should use generous timeouts and avoid asserting exact timing.

---

## Testing Considerations (Quick Reference)

This section summarizes the key testing challenges the ChatAssist API presents. These are explored in depth throughout the course.

| Challenge | Where It Shows Up | Course Session |
|-----------|-------------------|----------------|
| Non-deterministic output | Same prompt, different responses | Session 1, 2 |
| Choosing assertion strength | Exact match vs. semantic match vs. schema check | Session 2 |
| Token counting | Usage varies even for identical prompts | Session 1, 3 |
| Streaming validation | Concatenating chunks, handling mid-stream errors | Session 1, 3 |
| Schema adherence | Does structured output always match the schema? | Session 2, 3 |
| Tool call correctness | Does the model call the right function with valid args? | Session 2, 3 |
| Rate limit handling | Retry logic, backoff strategies | Session 0, 4 |
| Safety filter behavior | Threshold differences across safety levels | Session 3, 5 |
| Model version drift | Response quality changes when models update | Session 4 |
| Prompt injection | Adversarial input that manipulates model behavior | Session 5 |
| PII in responses | Model may generate or expose personal data | Session 5 |
| Cost awareness | Tests that accidentally burn through token quotas | Session 3, 4 |
