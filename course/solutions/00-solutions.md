# Session 0 Solutions: HTTP Decoder

> These are the solution notes for the Session 0 exercises. Do not distribute to participants before the session.

---

### Task 1

| Pair | Method | Endpoint | Status Code | Success or Failure? |
|------|--------|----------|-------------|---------------------|
| 1 | POST | /v1/chat/completions | 200 | Success |
| 2 | POST | /v1/chat/completions | 401 | Failure |
| 3 | POST | /v1/chat/completions | 400 | Failure |
| 4 | POST | /v1/chat/completions | 429 | Failure |
| 5 | POST | /v1/chat/completions | 200 | Success |

### Task 2

- **Pair 2 (401):** The API key `invalid-key-000` is not valid. It does not follow the `ca-key-{32 chars}` format. Fix: use a valid API key.
- **Pair 3 (400):** The temperature parameter is set to 3.5, which is outside the valid range of 0.0 to 2.0. Fix: set temperature to a value within range.
- **Pair 4 (429):** The client has exceeded its rate limit (0 of 60 requests remaining). Fix: wait 12 seconds (as specified by the `Retry-After` header) and retry.

### Task 3

- Answer text: `choices[0].message.content` = "The Pacific Ocean is the largest ocean on Earth, covering approximately 63 million square miles."
- Role: `choices[0].message.role` = "assistant"
- Finish reason: `choices[0].finish_reason` = "stop"
- Completion tokens: `usage.completion_tokens` = 22

### Task 4

- `Authorization: Bearer ca-key-abc123def456` -- Authenticates the request. The API key proves the client is authorized to use the API.
- `Content-Type: application/json` -- Tells the server/client that the body is formatted as JSON.
- `X-RateLimit-Remaining: 57` -- The client has 57 requests remaining in the current rate limit window.
- `Retry-After: 12` -- The client should wait 12 seconds before retrying.
- `X-RateLimit-Limit: 60` -- The maximum number of requests allowed per rate limit window is 60.

### Task 5

1. Prompt tokens = 98. This is higher than Pair 1 (13 tokens) because the request includes a system message, the original user question, the assistant's previous response, and the follow-up question. Multi-turn conversations accumulate tokens.
2. Completion tokens = 52.
3. Cost calculation:
   - Input: 98 tokens x ($2.00 / 1,000,000) = $0.000196
   - Output: 52 tokens x ($6.00 / 1,000,000) = $0.000312
   - Total: $0.000508 (approximately $0.0005 per request)
   - At this rate, 1,000 similar requests would cost about $0.51.
