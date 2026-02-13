# Session 0 Exercises: HTTP Decoder

**Duration:** 20 minutes
**Format:** Paper-based (no tools required)

---

## Setup

Below are five ChatAssist API request/response pairs. Some succeed, some fail. Your job is to read each one and answer the questions that follow.

---

### Pair 1: Simple Question

**Request:**
```
POST /v1/chat/completions HTTP/1.1
Host: api.chatassist.example
Authorization: Bearer ca-key-abc123def456
Content-Type: application/json

{
  "model": "chatassist-4",
  "messages": [
    {"role": "user", "content": "What is the largest ocean on Earth?"}
  ],
  "temperature": 0.0,
  "max_tokens": 100
}
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 57
X-TokenLimit-Remaining: 98500

{
  "id": "resp-001",
  "object": "chat.completion",
  "created": 1700002000,
  "model": "chatassist-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The Pacific Ocean is the largest ocean on Earth, covering approximately 63 million square miles."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 22,
    "total_tokens": 35
  }
}
```

---

### Pair 2: Authentication Failure

**Request:**
```
POST /v1/chat/completions HTTP/1.1
Host: api.chatassist.example
Authorization: Bearer invalid-key-000
Content-Type: application/json

{
  "model": "chatassist-4",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ]
}
```

**Response:**
```
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": {
    "type": "authentication_error",
    "message": "Invalid API key. Verify your API key at https://dashboard.chatassist.example/keys",
    "code": 401
  }
}
```

---

### Pair 3: Invalid Parameter

**Request:**
```
POST /v1/chat/completions HTTP/1.1
Host: api.chatassist.example
Authorization: Bearer ca-key-abc123def456
Content-Type: application/json

{
  "model": "chatassist-4",
  "messages": [
    {"role": "user", "content": "Tell me a joke."}
  ],
  "temperature": 3.5
}
```

**Response:**
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "type": "invalid_request",
    "message": "temperature must be between 0.0 and 2.0, got 3.5",
    "code": 400,
    "param": "temperature"
  }
}
```

---

### Pair 4: Rate Limited

**Request:**
```
POST /v1/chat/completions HTTP/1.1
Host: api.chatassist.example
Authorization: Bearer ca-key-abc123def456
Content-Type: application/json

{
  "model": "chatassist-4",
  "messages": [
    {"role": "user", "content": "Summarize today's news."}
  ]
}
```

**Response:**
```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 12
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700000072

{
  "error": {
    "type": "rate_limit_error",
    "message": "Rate limit exceeded. Try again in 12 seconds.",
    "code": 429
  }
}
```

---

### Pair 5: Multi-turn Conversation

**Request:**
```
POST /v1/chat/completions HTTP/1.1
Host: api.chatassist.example
Authorization: Bearer ca-key-abc123def456
Content-Type: application/json

{
  "model": "chatassist-4",
  "messages": [
    {"role": "system", "content": "You are a math tutor. Show your work step by step."},
    {"role": "user", "content": "What is 15% of 240?"},
    {"role": "assistant", "content": "To find 15% of 240:\n\nStep 1: Convert 15% to decimal: 15/100 = 0.15\nStep 2: Multiply: 0.15 x 240 = 36\n\nSo 15% of 240 is 36."},
    {"role": "user", "content": "Now what is 20% of the same number?"}
  ],
  "temperature": 0.3,
  "max_tokens": 150
}
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Remaining: 54

{
  "id": "resp-005",
  "object": "chat.completion",
  "created": 1700002500,
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

---

## Tasks

### Task 1: Identify the Basics

For each of the five pairs, fill in this table:

| Pair | Method | Endpoint | Status Code | Success or Failure? |
|------|--------|----------|-------------|---------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Task 2: Diagnose the Errors

For pairs 2, 3, and 4 (the error responses):

1. What went wrong in each case?
2. What should the client do to fix or recover from each error?

### Task 3: Trace the Answer

For Pair 1 (the successful response), trace the full path from the raw response to the answer text. Write the JSON path you would use to extract:

- The answer text itself
- The role of the responder
- The reason generation stopped
- The number of tokens the model generated

### Task 4: Inspect the Headers

Look at the headers across all five pairs. For each header listed below, explain what it tells you:

- `Authorization: Bearer ca-key-abc123def456`
- `Content-Type: application/json`
- `X-RateLimit-Remaining: 57`
- `Retry-After: 12`
- `X-RateLimit-Limit: 60`

### Task 5: Calculate Token Cost

Using Pair 5 (the multi-turn conversation):

1. How many tokens were in the prompt? Why might this number be higher than in Pair 1?
2. How many tokens did the model generate in its response?
3. If the ChatAssist API charges $2.00 per million input tokens and $6.00 per million output tokens, what is the cost of this single request? (Hint: calculate input and output costs separately, then add them.)

---

> **Solutions:** See `solutions/00-solutions.md` (instructor only).
