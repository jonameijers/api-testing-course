# Session 0: HTTP & API Fundamentals

**Duration:** 90 minutes
**Deliverable:** HTTP & API Cheat Sheet

## Learning Objectives

By the end of this session, you will be able to:

1. Describe the structure of an HTTP request and response
2. Identify the correct HTTP method for a given operation
3. Interpret common status codes (200, 400, 401, 403, 429, 500, 503)
4. Explain how authentication works with API keys and bearer tokens
5. Read and construct simple JSON request bodies
6. Explain what rate limiting is and why it matters for GenAI APIs

---

## Bridge from UI Testing (10 min)

If you have been writing Selenium, Cypress, or Playwright tests, you have been using HTTP every single day without seeing it. Every `driver.get()` call is an HTTP GET request. Every form submission is an HTTP POST. Every "page not found" error is a 404 status code. The browser handles all of this invisibly.

Here is how your familiar UI testing actions map to raw HTTP:

| What you do in UI testing | What is happening over HTTP |
|---|---|
| `driver.get(url)` | `GET /page` request to the server |
| Submit a form | `POST /endpoint` with a body containing the form data |
| "Page not found" in the browser | Server returned a `404 Not Found` status code |
| Login cookies keeping you authenticated | `Authorization: Bearer <token>` header sent with every request |

**Key insight:** API testing strips away the browser layer. Everything you have seen through the browser UI, you will now see as raw HTTP. It is the same data, just a different perspective. You already understand the concepts -- this session gives you the vocabulary.

---

## Section 1: The Request-Response Cycle (15 min)

All API communication follows a single pattern: the **client** sends a **request**, and the **server** returns a **response**. This is identical to what your browser does on every page load, but now you build the request yourself.

### Anatomy of an HTTP Request

Every request has four parts:

1. **Method** -- what action to take (GET, POST, PUT, DELETE)
2. **URL** -- where to send it (`https://api.chatassist.example/v1/chat/completions`)
3. **Headers** -- metadata about the request (authentication, content type)
4. **Body** -- the data you are sending (for POST/PUT requests)

### Anatomy of an HTTP Response

Every response has three parts:

1. **Status code** -- did it work? (200 = yes, 400 = your fault, 500 = their fault)
2. **Headers** -- metadata about the response (rate limits, content type)
3. **Body** -- the actual data returned (usually JSON)

### A Complete ChatAssist API Call

Here is a real request and response, end to end.

**Request:**
```
POST /v1/chat/completions HTTP/1.1
Host: api.chatassist.example
Authorization: Bearer ca-key-abc123def456
Content-Type: application/json

{
  "model": "chatassist-4",
  "messages": [
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.0,
  "max_tokens": 50
}
```

**Response:**
```
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Remaining: 58

{
  "id": "resp-ex1-001",
  "object": "chat.completion",
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

In your browser, this entire exchange happens invisibly. In API testing, you construct the request, send it, and inspect the response yourself.

---

## Section 2: HTTP Methods and When They Matter (10 min)

HTTP defines several methods (also called "verbs") that indicate what you want the server to do:

| Method | Purpose | Idempotent? | Example |
|--------|---------|-------------|---------|
| `GET` | Retrieve data | Yes | Get a list of available models |
| `POST` | Send data to create or generate something | No | Send a prompt, receive a completion |
| `PUT` | Replace a resource entirely | Yes | Replace a configuration |
| `PATCH` | Update part of a resource | Depends | Update one field in a record |
| `DELETE` | Remove a resource | Yes | Delete a saved conversation |

**Why GenAI APIs primarily use POST:** You are sending data (your prompt) to generate something new (the completion). That is the definition of POST. Unlike a traditional REST API where you might GET a user's profile, a GenAI API generates a response that did not exist before you asked.

**Idempotency matters for testing:** If you send the same GET request twice, you get the same data both times. But if you send the same POST to a GenAI API twice, you may get two *different* completions -- and that is by design, not a bug. This is a fundamental shift from traditional API testing and a concept we will explore deeply in Session 1.

**ChatAssist API note:** All chat operations use `POST /v1/chat/completions`. The simplicity is typical of GenAI APIs -- a single endpoint handles many types of requests, controlled by the request body rather than different URLs.

---

## Section 3: Status Codes -- The Language of Success and Failure (10 min)

Status codes are three-digit numbers that tell you what happened. They fall into groups:

### 2xx: Success -- it worked

- **200 OK** -- your request succeeded, and the response body contains the result

### 4xx: Client errors -- something in *your* request is wrong

- **400 Bad Request** -- your request is malformed or has invalid parameters
- **401 Unauthorized** -- your API key is missing or invalid
- **403 Forbidden** -- your API key is valid but does not have permission for this operation
- **429 Too Many Requests** -- you have hit a rate limit

### 5xx: Server errors -- something on *their* end is wrong

- **500 Internal Server Error** -- the server failed unexpectedly
- **503 Service Unavailable** -- the server (or model) is overloaded

### ChatAssist Error Examples

Each error from the ChatAssist API has a consistent JSON format with a `type`, `message`, and `code`:

**400 -- Invalid parameter:**
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

**401 -- Bad API key:**
```json
{
  "error": {
    "type": "authentication_error",
    "message": "Invalid API key. Verify your API key at https://dashboard.chatassist.example/keys",
    "code": 401
  }
}
```

**429 -- Rate limited:**
```json
{
  "error": {
    "type": "rate_limit_error",
    "message": "Rate limit exceeded. Try again in 12 seconds.",
    "code": 429
  }
}
```

**500 -- Server error:**
```json
{
  "error": {
    "type": "server_error",
    "message": "An internal error occurred. Please retry your request.",
    "code": 500
  }
}
```

As a tester, you will write test cases for *all* of these. The happy path (200) is only the starting point -- error handling is where most bugs hide.

### Rate Limiting: A Bigger Deal Than You Think

Rate limiting exists on traditional APIs too, but GenAI APIs have **dual rate limits** that make it a much bigger concern:

- **Requests per minute** -- how many calls you can make (e.g., 60 req/min on Standard tier)
- **Tokens per minute** -- how many tokens you can consume (e.g., 100,000 tokens/min on Standard tier)

You can hit either limit independently. A test suite that sends 50 short requests might be fine on request count but a test suite that sends 5 very long prompts might blow through the token limit. The ChatAssist API has three tiers:

| Tier | Requests/min | Tokens/min | Tokens/day |
|------|-------------|------------|------------|
| Free | 10 | 10,000 | 100,000 |
| Standard | 60 | 100,000 | 2,000,000 |
| Enterprise | 300 | 1,000,000 | unlimited |

---

## Section 4: Headers and Authentication (10 min)

Headers carry metadata about requests and responses. Three header types matter most for API testing.

### Content-Type

Tells the server what format your request body is in:
```
Content-Type: application/json
```

Almost every GenAI API uses JSON. You will set this header on every request.

### Authorization

Identifies who you are. The ChatAssist API uses **bearer token authentication** -- your API key is sent in the Authorization header:

```
Authorization: Bearer ca-key-abc123def456
```

API keys follow the format `ca-key-{32 alphanumeric characters}`. This is simpler than the login flows you know from UI testing -- no cookies, no session management. You include the key in every request, and the server validates it every time.

**Security warning:** API key security is a critical concern. Research shows that nearly 22% of files uploaded to AI tools contain sensitive content, and hardcoded API keys in test scripts are one of the most common security mistakes. Never commit API keys to version control. Use environment variables or secrets management instead.

### Rate Limit Headers

The response includes headers that tell you your rate limit status:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1700000060
X-TokenLimit-Remaining: 95420
```

When you hit a rate limit (429), the response also includes:
```
Retry-After: 12
```

This tells you how many seconds to wait before retrying. Your test infrastructure should respect this -- do not just hammer the API with retries.

---

## Section 5: JSON -- Reading and Writing API Data (10 min)

JSON (JavaScript Object Notation) is the standard data format for APIs. If you have worked with web applications, you have probably encountered JSON already. Here is a quick review of the building blocks.

### JSON Data Types

| Type | Example | Notes |
|------|---------|-------|
| String | `"hello"` | Always in double quotes |
| Number | `42`, `3.14` | No quotes |
| Boolean | `true`, `false` | No quotes, lowercase |
| Null | `null` | Represents "no value" |
| Object | `{"key": "value"}` | Curly braces, key-value pairs |
| Array | `[1, 2, 3]` | Square brackets, ordered list |

### Navigating Nested JSON

API responses are almost always nested objects. You navigate them using dot notation and array indices. Here is a ChatAssist response and how to reach each piece of data:

```json
{
  "id": "resp-ex1-001",
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

| What you want | Path | Value |
|---------------|------|-------|
| The response ID | `id` | `"resp-ex1-001"` |
| The answer text | `choices[0].message.content` | `"The capital of France is Paris."` |
| The assistant's role | `choices[0].message.role` | `"assistant"` |
| Why generation stopped | `choices[0].finish_reason` | `"stop"` |
| Total tokens used | `usage.total_tokens` | `18` |

The path `choices[0].message.content` is the single most important path in GenAI API testing -- it is where the model's answer lives. You will use this path in virtually every test.

### The Usage Object

Every ChatAssist response includes a `usage` object that tells you how many tokens were consumed:

- `prompt_tokens` -- tokens in your input (what you sent)
- `completion_tokens` -- tokens in the output (what the model generated)
- `total_tokens` -- the sum of both

This matters because GenAI APIs charge by the token. A test suite that runs 1,000 requests at 500 tokens each consumes 500,000 tokens. Understanding token usage is part of responsible test design.

---

## Discussion and Q&A (15 min)

Consider these questions as you reflect on the session:

- What HTTP concepts were you already using without realizing it?
- How does seeing raw HTTP change your understanding of what your UI tests do?
- When might you need to test at the API level instead of the UI level?
- What would happen to your test suite if the API started returning 429 errors mid-run?

---

## Session Deliverable: HTTP & API Cheat Sheet

This session's deliverable is a one-page reference you can keep at your desk:

**HTTP Methods Quick Reference**

| Method | Purpose | Idempotent? |
|--------|---------|-------------|
| GET | Retrieve data | Yes |
| POST | Create/generate | No |
| PUT | Replace | Yes |
| PATCH | Partial update | Depends |
| DELETE | Remove | Yes |

**Status Codes Quick Reference**

| Code | Meaning | Category |
|------|---------|----------|
| 200 | OK | Success |
| 400 | Bad Request | Client error |
| 401 | Unauthorized | Client error |
| 403 | Forbidden | Client error |
| 429 | Too Many Requests | Client error (rate limit) |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Server error |

**Request Anatomy:**
Method + URL + Headers (Authorization, Content-Type) + Body (JSON)

**Response Anatomy:**
Status Code + Headers (Rate limits, Content-Type) + Body (JSON)

**Authentication:** `Authorization: Bearer ca-key-abc123def456`

**Key JSON Path:** `choices[0].message.content` -- where the answer lives

**Rate Limit Headers:** `X-RateLimit-Remaining`, `X-TokenLimit-Remaining`, `Retry-After`
