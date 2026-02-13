# GenAI API Differences Cheat Sheet

> One-page reference: what behaves deterministically, probabilistically, and policy-dependently in GenAI APIs.

---

## At a Glance: Three Categories of API Behavior

| Category | Definition | Testability |
|----------|-----------|-------------|
| **Deterministic** | Same input always produces the same output. Can be asserted with exact match. | High -- traditional assertions work |
| **Probabilistic** | Same input produces variable output by design. Requires flexible assertions. | Medium -- use semantic/statistical checks |
| **Policy-Dependent** | Behavior depends on provider-configured rules that change over time. | Low -- must monitor for drift |

---

## Two-Column Comparison: Traditional API vs. GenAI API

| Traditional REST API | GenAI API |
|---------------------|-----------|
| Same input, same output | Same input, different output (by design) |
| Fixed response schema | Response content varies; schema can be enforced with structured output mode |
| Errors are clearly wrong | Model "errors" may look like valid responses (hallucinations) |
| Versioning is explicit (v1, v2) | Model versions drift silently; aliases like "latest" change behavior |
| Cost per request is flat or free | Cost per request varies by token count (input + output) |
| Rate limits count requests | Rate limits count both requests AND tokens |
| Test data is static fixtures | Test data must account for prompt phrasing sensitivity |
| Latency is predictable | Latency depends on output length, model load, and prompt complexity |
| Binary pass/fail assertions | Graded assertions with thresholds and scoring |
| Security = input validation | Security = input validation + prompt injection + output sanitization |

---

## Deterministic Behaviors (Safe to Assert Exactly)

These work the same way every time. Use exact-match assertions.

| Behavior | What to Assert | Example |
|----------|---------------|---------|
| HTTP status codes | `response.status == 200` | 200, 400, 401, 429, 500, 503 |
| Response structure | Required fields exist with correct types | `choices[0].message.role == "assistant"` |
| Error response format | Error object has `type`, `message`, `code` | `error.code == 429` |
| Rate limit headers | Header values are present and numeric | `X-RateLimit-Remaining` is an integer |
| Finish reason values | One of the documented enum values | `stop`, `length`, `tool_calls`, `safety` |
| Structured output schema | Parsed JSON matches the provided schema | All `required` fields present, correct types |
| Tool call function name | Model calls a documented function | `tool_calls[0].function.name == "lookup_order"` |
| Token usage fields | `prompt_tokens`, `completion_tokens`, `total_tokens` are positive integers | `usage.total_tokens > 0` |
| Authentication rejection | Missing/invalid key returns 401 | `error.type == "authentication_error"` |
| Parameter validation | Out-of-range values return 400 | `temperature: 3.5` returns invalid_request |

---

## Probabilistic Behaviors (Require Flexible Assertions)

These vary by design. Use containment, similarity, or statistical assertions.

| Behavior | Why It Varies | How to Assert |
|----------|--------------|---------------|
| Response wording | Token sampling is random | Containment: check for key terms, not exact text |
| Response length | Model decides when to stop | Range check: `10 < word_count < 500` |
| Explanation style | Model has multiple valid phrasings | Semantic similarity against a reference |
| Tool call arguments | Model extracts values from context | Validate argument types and plausibility |
| Creativity/tone | Temperature and top_p affect sampling | LLM-as-judge or human review |
| Multi-turn coherence | Context window management varies | Check that key facts persist across turns |
| Streaming chunk sizes | Network and model internals vary | Validate: all chunks form valid complete response |
| Completion token count | Different wordings use different tokens | Range assertion: `20 < completion_tokens < 200` |

---

## Policy-Dependent Behaviors (Monitor for Drift)

These change when the provider updates models, safety filters, or policies. No code change on your side triggers the change.

| Behavior | What Can Change | How to Detect |
|----------|----------------|---------------|
| Safety filter thresholds | Content blocked today may pass tomorrow (or vice versa) | Run a "canary" safety test suite daily |
| Model knowledge cutoff | Model may know/not know recent facts | Track factual accuracy scores over time |
| Default model alias | `chatassist-4` may point to a different version | Log `response.model` and compare to request |
| Refusal behavior | Model may become more or less cautious | Track refusal rate for borderline prompts |
| Output formatting | Model may start adding markdown, lists, etc. | Structural assertions on format patterns |
| Token pricing | Cost per token changes with model updates | Track `usage` values and compute costs per run |
| Deprecation | Entire model versions get retired | Monitor provider deprecation announcements |
| Rate limit tiers | Quotas may change per plan | Check `X-RateLimit-Limit` header periodically |

---

## Quick Decision Matrix: How Should I Test This?

| If you need to verify... | Category | Assertion Type | Stability |
|--------------------------|----------|---------------|-----------|
| Response is valid JSON | Deterministic | Exact / structural | High |
| Response mentions "Paris" | Probabilistic | Containment | High |
| Response is a helpful answer | Probabilistic | LLM-as-judge | Low |
| Error code is 429 | Deterministic | Exact match | High |
| Safety filter blocks harmful content | Policy-dependent | Expected finish_reason + monitoring | Medium |
| Model calls the correct tool | Probabilistic | Exact function name + argument validation | Medium |
| Response quality hasn't degraded | Policy-dependent | Statistical trend over time | Low |
| Structured output matches schema | Deterministic | JSON Schema validation | High |
| Response doesn't contain PII | Probabilistic | Negative containment + regex | Medium |
| Cost per request is within budget | Probabilistic | Range assertion on usage.total_tokens | Medium |

---

## Key Numbers to Remember

| Metric | Typical Value | Why It Matters |
|--------|--------------|----------------|
| Temperature range | 0.0 -- 2.0 | 0 = near-deterministic, 2 = maximum randomness |
| Context window (large model) | 128K tokens | Exceeding it returns 400 |
| Context window (small model) | 8K -- 32K tokens | Cheaper but more limited |
| Streaming time-to-first-token | 100 -- 500ms | User-perceived responsiveness |
| Short completion latency | 200 -- 800ms | Set test timeouts accordingly |
| Long completion latency | 3 -- 15s | Do not use short timeouts |
| Rate limit (standard tier) | 60 req/min, 100K tokens/min | Both limits apply simultaneously |

---

*This cheat sheet is a companion to Session 1: How GenAI APIs Differ from Normal APIs. Refer to the ChatAssist API Specification for detailed endpoint documentation.*
