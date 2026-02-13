# HTTP & API Cheat Sheet

> Quick reference for API testing fundamentals. Produced in Session 0.

---

## HTTP Methods

| Method | Purpose | Idempotent? | GenAI API Usage |
|--------|---------|-------------|-----------------|
| GET | Retrieve data | Yes | List models, check status |
| POST | Create/generate | No | Send prompts, create completions |
| PUT | Replace a resource | Yes | Replace configurations |
| PATCH | Partial update | Depends | Update individual settings |
| DELETE | Remove a resource | Yes | Delete saved conversations |

**GenAI APIs primarily use POST** -- you send data (a prompt) to generate something new (a completion).

---

## Status Codes

| Code | Meaning | Category | What to Do |
|------|---------|----------|------------|
| 200 | OK | Success | Validate the response body |
| 400 | Bad Request | Client error | Check your request parameters |
| 401 | Unauthorized | Client error | Check your API key |
| 403 | Forbidden | Client error | Check permissions/tier |
| 429 | Too Many Requests | Rate limit | Wait (check Retry-After header) |
| 500 | Internal Server Error | Server error | Retry with backoff |
| 503 | Service Unavailable | Server error | Model overloaded, retry later |

**Rule of thumb:** 2xx = success, 4xx = your fault, 5xx = their fault.

---

## Request Anatomy

```
METHOD /endpoint HTTP/1.1
Host: api.example.com
Authorization: Bearer <api-key>
Content-Type: application/json

{
  "model": "model-name",
  "messages": [...],
  "temperature": 0.0,
  "max_tokens": 100
}
```

**Four parts:** Method + URL + Headers + Body

---

## Response Anatomy

```
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Remaining: 58

{
  "choices": [{ "message": { "content": "..." }, "finish_reason": "stop" }],
  "usage": { "prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18 }
}
```

**Three parts:** Status Code + Headers + Body

---

## Key Headers

| Header | Direction | Purpose |
|--------|-----------|---------|
| `Authorization: Bearer <key>` | Request | Authenticate your API call |
| `Content-Type: application/json` | Both | Body is JSON format |
| `X-RateLimit-Limit` | Response | Max requests per window |
| `X-RateLimit-Remaining` | Response | Requests left in window |
| `X-TokenLimit-Remaining` | Response | Tokens left in window |
| `Retry-After` | Response (429) | Seconds to wait before retry |

---

## Authentication

GenAI APIs use **Bearer token authentication**:

```
Authorization: Bearer ca-key-abc123def456
```

- Included in every request
- No cookies, no sessions, no CSRF
- **Never commit API keys to version control**
- Use environment variables or secrets management

---

## JSON Quick Reference

| Type | Example | Notes |
|------|---------|-------|
| String | `"hello"` | Always double quotes |
| Number | `42`, `3.14` | No quotes |
| Boolean | `true`, `false` | Lowercase, no quotes |
| Null | `null` | Represents "no value" |
| Object | `{"key": "value"}` | Curly braces |
| Array | `[1, 2, 3]` | Square brackets |

**The most important JSON path in GenAI API testing:**

```
choices[0].message.content    -- where the model's answer lives
```

---

## Rate Limits (GenAI-Specific)

GenAI APIs have **dual rate limits**:

1. **Requests per minute** -- how many calls you can make
2. **Tokens per minute** -- how many tokens you can consume

You can hit either limit independently. A few long prompts can exhaust the token limit even if you are well within the request limit.

---

## Token Basics

- Tokens are subword units (~4 characters in English)
- `"hello"` = 1 token; `"unbelievable"` = ~3 tokens
- Tracked per response in the `usage` object:
  - `prompt_tokens` -- what you sent
  - `completion_tokens` -- what the model generated
  - `total_tokens` -- the sum
- Tokens = billing unit, context limit unit, and rate limit unit
