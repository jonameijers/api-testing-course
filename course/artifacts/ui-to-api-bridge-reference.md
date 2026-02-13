# UI-to-API Bridge Reference

> Three-column comparison mapping familiar UI testing concepts to their API and GenAI API equivalents. Designed for testers transitioning from UI automation (Selenium, Playwright, Cypress) to GenAI API testing.

---

## Assertions

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| `expect(element.text).toBe("Add to Cart")` | `expect(response.body.name).toBe("Widget")` | Exact match rarely works. Use containment, similarity, or LLM-as-judge instead. |
| `expect(element.text).toContain("Cart")` | `expect(response.body.description).toContain("widget")` | `expect(response.content).toContain("Paris")` -- check for key facts, not exact wording. |
| `expect(element).toBeVisible()` | `expect(response.status).toBe(200)` | `expect(response.status).toBe(200)` AND `expect(choices[0].finish_reason).toBe("stop")` |
| `expect(element).toHaveAttribute("href", "/cart")` | `expect(response.body.id).toBeNumber()` | `expect(usage.total_tokens).toBeGreaterThan(0)` -- validate structure and metadata. |
| Screenshot diff with tolerance (e.g., 5% pixel difference) | JSON schema validation | Semantic similarity with threshold (e.g., cosine >= 0.85). Same concept: fuzzy comparison. |
| No UI equivalent | No traditional equivalent | **LLM-as-judge**: ask another model to grade the response quality. New assertion type unique to GenAI. |
| Run test once; it should always pass | Run test once; it should always pass | Run test 5 times; assert it passes 4+ times. Non-determinism requires statistical pass criteria. |

### Key Insight

Your assertion instincts transfer directly. The difference is that GenAI testing extends the ladder upward with two new levels (similarity-based and LLM-as-judge) and shifts the "sweet spot" from exact matching to flexible matching.

---

## Test Data

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| Static HTML fixtures, mock servers | JSON fixture files, mock API responses | **Prompt templates** with variable inputs. The "test data" is the prompt itself. |
| Test database seeded with known data | Predefined request/response pairs | Predefined prompts with expected behaviors (not exact expected outputs). |
| Page Object Model encapsulates selectors | Request builders encapsulate endpoints | **Prompt builders** encapsulate system prompts, message templates, and parameters. |
| Test data is deterministic (same seed = same page) | Test data is deterministic (same request = same response) | Test data is deterministic, but the response is NOT. Same prompt can give different answers. |
| Generate test data with factories (Faker, FactoryBot) | Generate request payloads programmatically | Generate prompt variations programmatically. BUT: never use real PII -- use synthetic data only. |
| Sensitive data mocked/anonymized | API keys in environment variables | API keys in environment variables. PLUS: never put real customer data in prompts. |

### Key Insight

Test data management is similar, but you must treat prompts as sensitive artifacts (they may contain business logic) and treat real PII as forbidden in any test prompt.

---

## Fixtures and Setup

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| `beforeEach`: navigate to page, log in | `beforeEach`: set auth headers, create base URL | `beforeEach`: set API key, configure model, set temperature and max_tokens. |
| Page Object Model organizes selectors | API client abstraction layer | **Model client** wrapping: endpoint, auth, default parameters, retry logic. |
| Browser setup (Chrome, Firefox, headless) | HTTP client setup (Axios, requests, RestAssured) | Same HTTP client as API testing. No special framework needed at the transport level. |
| Mock server for third-party services | Mock server for downstream APIs | Mock server for tool call results. Model calls `lookup_order` -- your mock returns a fixed JSON response. |
| Database seed and teardown | Database seed and teardown | Mostly stateless (no database to seed). BUT: may need to manage conversation state for multi-turn tests. |
| Clean browser state between tests | Clean session/auth state between tests | Fresh conversation (empty messages array) between tests. Beware of shared rate limits across parallel tests. |

### Key Insight

Fixtures are simpler for GenAI API testing (no browser, no DOM). The main new concern is managing rate limits across concurrent tests and ensuring fresh conversation state.

---

## Flakiness

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| **Root cause:** Timing. Element not yet visible; animation not complete; CDN slow. | **Root cause:** Environment. Server restart; database state; network latency. | **Root cause:** Randomness. Model produces different valid answers from the same prompt (by design). |
| **Fix:** Add explicit waits, retry on stale element, increase timeout. | **Fix:** Retry with backoff, ensure test isolation, fix test order dependencies. | **Fix:** Use softer assertions (containment, similarity), statistical pass criteria (4/5), lower temperature. |
| Retry the click/action | Retry the HTTP request | Retry the API call AND accept that different (valid) responses are not failures. |
| Flakiness = a bug to fix | Flakiness = usually environment | Flakiness = sometimes expected behavior. The model is non-deterministic. Not all variance is a bug. |
| CI/CD: rerun failed test once | CI/CD: rerun with backoff | CI/CD: rerun N times, pass if threshold met. Track pass rates over time. |
| `waitForElement()` | `retry(3, { delay: 1000 })` | `retryWithBackoff()` for 429/500 errors + `statisticalPass(runs=5, minPassing=4)` for non-determinism. |

### Key Insight

You already know how to debug flaky tests. The root causes shift from timing/environment to model randomness/drift. The diagnostic instinct is the same: is this a real bug, an environment issue, or a test design problem?

---

## Coverage

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| Pages x browsers x devices x user flows | Endpoints x methods x status codes x auth paths | **Modes x parameters x input types x model versions x safety levels** |
| "Did we test every page?" | "Did we test every endpoint?" | "Did we test every mode (completion, structured, tools, streaming)?" |
| "Did we test on Chrome, Firefox, Safari?" | "Did we test with valid and invalid auth?" | "Did we test with temperature 0 and temperature 2? With different models?" |
| "Did we test the happy path and error states?" | "Did we test 200, 400, 401, 404, 500?" | "Did we test 200, 400, 401, 429, 500, 503, AND safety blocks, AND truncation?" |
| Cross-browser testing matrix | API endpoint matrix | **Coverage matrix**: mode x dimension x priority x assertion level x CI/CD tier. |
| Visual regression (screenshot comparison) | Schema validation (contract testing) | Schema validation PLUS semantic regression (quality scores trending over time). |
| No equivalent | No equivalent | **Adversarial coverage**: prompt injection, PII extraction, system prompt leakage, tool abuse. |
| Code coverage (lines, branches) | Code coverage + endpoint coverage | Code coverage is less meaningful. Focus on **behavioral coverage** and **risk coverage**. |

### Key Insight

Coverage for GenAI APIs has more dimensions than UI or traditional API testing. The combinatorial explosion comes from modes x parameters x input types x model versions, plus a new adversarial dimension that has no UI testing equivalent.

---

## Reporting

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| Pass/fail per test case | Pass/fail per test case | Pass/fail PLUS **quality scores** per test case (similarity, judge score, pass rate). |
| Screenshot on failure | Request/response log on failure | Request/response log PLUS model version, token usage, latency, and assertion scores. |
| HTML test report (Allure, Extent) | HTML/JSON report | HTML/JSON report PLUS **evaluation dashboard** tracking scores over time. |
| Failure = definite bug | Failure = definite bug | Failure = maybe a bug, maybe flakiness, maybe drift. **Triage is required.** |
| Trend: pass rate over time | Trend: pass rate over time | Trend: pass rate + quality score + token cost + latency + model version -- all over time. |
| Defect filed per failure | Defect filed per failure | Defect filed only after triage. Many failures are flakiness, not bugs. |

### Key Insight

Reporting for GenAI testing is richer. You track quality scores, token costs, and model versions alongside pass/fail. The triage step between "test failed" and "file a bug" is essential -- not every failure is a defect.

---

## CI/CD

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| Run all tests on every PR | Run all tests on every PR | **Tiered approach**: fast tests on every PR, full suite nightly, deep evaluation pre-release. |
| Tests are free to run (local browser) | Tests are free to run (mock server) | **Tests cost money.** Every API call consumes tokens. Track cost per pipeline run. |
| Parallel execution across browsers | Parallel execution across endpoints | Parallel execution limited by **rate limits** (requests/min AND tokens/min). |
| Test environment = browser + app server | Test environment = HTTP client + app server | Test environment = HTTP client + API key + rate limit budget. No local server needed (unless mocking). |
| Pipeline: build -> unit -> e2e -> deploy | Pipeline: build -> unit -> API tests -> deploy | Pipeline: build -> unit -> **fast evals** -> quality gate -> deploy -> **monitor** -> feedback loop. |
| Quality gate: all tests pass | Quality gate: all tests pass | Quality gate: **score threshold met** (e.g., accuracy >= 0.8), not necessarily 100% pass rate. |
| No cost concern | No cost concern | **Cost guard**: abort pipeline if token spend exceeds budget. |

### Key Insight

CI/CD for GenAI testing adds two major concerns: every test costs money (token consumption) and rate limits constrain parallelism. The tiered approach (fast/standard/deep) manages these constraints.

---

## Security

| UI Testing | API Testing | GenAI API Testing |
|-----------|-------------|-------------------|
| Test for XSS (cross-site scripting) | Test for SQL injection, CSRF | Test for **prompt injection** (the "SQL injection of AI"). |
| Validate form inputs client-side | Validate request inputs server-side | Validate inputs AND validate **model outputs** before downstream use. |
| Check for sensitive data in page source | Check for sensitive data in responses | Check for PII in responses AND check for **system prompt leakage**. |
| HTTPS, CORS, CSP headers | Auth tokens, API keys, HTTPS | API keys + **prompt-level security** (adversarial input resistance). |
| OWASP Top 10 (Web) | OWASP Top 10 (Web) + API Security Top 10 | **OWASP Top 10 for LLM Applications 2025** -- a dedicated framework for GenAI. |
| Test RBAC (role-based access) | Test authorization levels | Test **agent privilege boundaries**: can the model call tools it shouldn't? |
| Input validation testing | Input validation + output validation | Input validation + output sanitization + **adversarial red teaming**. |
| No equivalent | No equivalent | **Data governance**: classify what data can be sent to external LLM APIs. |

### Key Insight

Security testing for GenAI APIs extends traditional security testing with prompt injection, output sanitization, system prompt protection, and data governance. The core principle is the same: never trust user input. The attack surface has expanded from forms and URLs to prompts, tool arguments, and model outputs.

---

## Skills That Transfer Directly

These UI testing skills apply to GenAI API testing with little or no modification:

- **Test design thinking**: Breaking features into testable scenarios
- **Debugging instincts**: Is this a real bug, environment issue, or test problem?
- **Automation architecture**: Page Object Model concepts apply to prompt/client abstractions
- **CI/CD pipeline design**: Same tools, same workflow, new quality gates
- **Security mindset**: Never trust user input (now: never trust model output either)
- **Reporting and communication**: Same stakeholders, same need for clear results

## Skills That Need Adaptation

These skills transfer but require adjustment:

- **Assertion writing**: From exact match to flexible matching with thresholds
- **Flakiness debugging**: From timing issues to randomness and drift
- **Coverage planning**: From pages and browsers to modes, parameters, and model versions
- **Cost awareness**: Tests are no longer free to run

## New Skills to Build

These are genuinely new for GenAI API testing:

- **Prompt engineering**: Writing effective prompts and system prompts
- **Evaluation design**: Creating scoring functions and judge prompts
- **Token economics**: Understanding and managing token costs
- **Model version management**: Tracking and responding to model changes
- **Adversarial testing**: Red teaming for prompt injection and data exfiltration

---

*This reference is introduced in Session 1 and updated throughout the course. It serves as a bridge between your existing expertise and the new domain.*
