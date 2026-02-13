# Session 3: Coverage Model

**Duration:** 90 minutes
**Deliverable:** Coverage Matrix Template

---

## Learning Objectives

By the end of this session, you will be able to:

1. Define what "coverage" means for a GenAI API (it is not code coverage)
2. Identify the six test dimensions specific to GenAI APIs
3. Prioritize test cases by risk, cost, and assertion difficulty
4. Design a coverage matrix for the ChatAssist API
5. Explain the tiered evaluation strategy (fast, standard, deep)

---

## Bridge from UI Testing (10 min)

**What you know from UI testing:**
In UI testing, coverage means asking questions like: Did we test every page? Every form? Every user flow? Every browser? You think in terms of pages, elements, and user journeys. The combinatorial explosion comes from pages multiplied by browsers multiplied by devices, and you manage it with risk-based prioritization.

**How this translates to GenAI API testing:**
Coverage still means "did we exercise what matters?" But the dimensions change:

| UI Testing Coverage | GenAI API Testing Coverage |
|---|---|
| Pages and user flows | API modes (completion, structured output, tool calling, streaming) |
| Form fields and validation rules | Parameter ranges (temperature, max_tokens, model selection) |
| Browser and device combinations | Model versions and configuration variants |
| Error states (404, JS errors) | Error paths (401, 429, 500, safety blocks) |
| Accessibility checks | Adversarial inputs (prompt injection, PII extraction) |
| Visual regression | Behavioral consistency across runs |

**Key insight:** In UI testing, you know the answer is wrong when the button says "Sumbit" instead of "Submit." In GenAI API testing, the combinatorial explosion comes from modes multiplied by parameters multiplied by input types multiplied by model versions. And you add a dimension that UI testing never has: *how do you know if the response is "right"?*

---

## Section 1: What "Coverage" Means for GenAI APIs (10 min)

Traditional test coverage dimensions still apply. You need endpoint coverage (are all endpoints tested?), status code coverage (do you test success and every documented error?), authentication paths (valid key, invalid key, expired key, missing key), and input validation (required fields missing, wrong types, out-of-range values). These are the same questions you would ask about any REST API.

But GenAI APIs add new dimensions that have no equivalent in traditional API testing. We organize these into a **six-axis coverage map**.

### The Six-Axis Coverage Map

**Axis 1 -- Input Modality**
What kinds of input does the API accept, and are you testing all of them?

- Single-turn text prompts (the simplest case)
- Multi-turn conversations (context accumulation across messages)
- System prompts with varying instructions
- Inputs with embedded data (documents to summarize, reviews to classify)
- Multimodal inputs if the API supports them (images, audio)

For the ChatAssist API, this means testing with simple questions like "What is the capital of France?" but also with multi-turn conversations like the math tutor example, and with system prompts that set specific behavior ("You are a customer support agent...").

**Axis 2 -- Response Mode**
The ChatAssist API supports four modes, each with distinct testing needs:

| Mode | What to Test | Unique Challenges |
|---|---|---|
| Chat completion | Content quality, relevance, safety | Non-determinism in wording |
| Structured output | Schema adherence, field correctness | Parsing the JSON string inside `content` |
| Tool calling | Correct tool selection, valid arguments, multi-step flows | The model might pick the wrong tool or hallucinate parameters |
| Streaming | Chunk reassembly, mid-stream errors, `[DONE]` signal | Time-based behavior, partial failure states |

If your test suite only covers chat completion, you have a significant gap when the application also uses tool calling and structured output.

**Axis 3 -- Output Contract**
What does "correct" look like for each test? This connects directly to the assertion ladder from Session 2:

- Structural correctness: valid JSON, required fields present, correct types
- Content accuracy: factual correctness, required keywords present
- Behavioral compliance: follows the system prompt instructions, uses the right tone
- Schema conformance: for structured output, exact match against the JSON Schema

**Axis 4 -- Safety Regime**
The ChatAssist API has three safety levels (`strict`, `standard`, `minimal`) and six safety categories. Your coverage should include:

- Each safety level with borderline content
- Each safety category with content designed to trigger it
- Verifying that `finish_reason: "safety"` appears when it should
- Verifying that legitimate content is *not* blocked (false positive testing)

**Axis 5 -- Failure Modes**
Every documented error deserves at least one test:

- `400` -- malformed JSON, invalid parameters, context window exceeded, invalid schema
- `401` -- missing key, invalid key
- `403` -- model access denied
- `429` -- rate limited (request quota), token quota exceeded
- `500` -- internal server error
- `503` -- model overloaded

Beyond HTTP errors, test for GenAI-specific failures:
- `finish_reason: "length"` (response truncated by `max_tokens`)
- `finish_reason: "safety"` (response blocked by safety filter)
- Mid-stream errors during streaming
- Tool call failures (tool returns an error, tool times out)

**Axis 6 -- Non-Functional Concerns**
These are easy to overlook but matter in production:

- **Latency**: Is the response time within acceptable bounds? (ChatAssist spec: 200-800ms for short completions, up to 15s for long ones)
- **Cost**: What is the token consumption per test? Track `usage.total_tokens`
- **Consistency**: Run the same test 5 times -- how much does the output vary?
- **Rate limit behavior**: Does the system handle `429` responses gracefully?
- **Model version sensitivity**: Does the test still pass against `chatassist-4-mini` and `chatassist-3`?

---

## Section 2: Auditing an Unknown Project (15 min)

When you join a team that already has GenAI API tests, how do you find the gaps? This is one of the first tasks you will face.

### The Coverage Audit Process

**Step 1: Inventory what exists.**
Read every test and categorize it by the six axes. For each test, note:
- Which mode does it test? (completion / structured / tool calling / streaming)
- Which assertion level does it use? (structural / containment / similarity / LLM-as-judge / statistical)
- What kind of input does it send? (simple / multi-turn / adversarial)
- What error paths does it cover?
- Does it test safety at all?

**Step 2: Build the coverage matrix.**
Create a table with the six axes as rows and the possible values as columns. Mark which cells have tests and which are empty.

**Step 3: Identify the common gaps.**
In practice, most GenAI API test suites share the same blind spots:

| Common Gap | Why It Matters |
|---|---|
| Only testing chat completion mode | Structured output and tool calling have distinct failure modes |
| No adversarial inputs | Prompt injection is the #1 LLM vulnerability (OWASP LLM01) |
| No negative assertions | Tests check what should be present but not what should be absent |
| No multi-turn tests | Context accumulation bugs only appear in conversations |
| No cost tracking | Token consumption surprises during CI/CD |
| Only testing the happy path | Error handling is where production incidents happen |
| No consistency checks | A test that passes once but fails the next 4 times is not reliable |

**Step 4: Prioritize and plan.**
Not every gap needs immediate attention. Prioritize using the risk framework from the next section.

### ChatAssist Audit Example

Imagine you join a team and find these 8 existing tests for the ChatAssist API:

1. Send a simple question, check that `status == 200`
2. Send a question, check that `choices[0].message.content` is not empty
3. Send an invalid API key, check for `401`
4. Send a structured output request, validate the response parses as JSON
5. Send a tool calling request, check that `finish_reason == "tool_calls"`
6. Send the tool result back, check that a final answer is returned
7. Check that `usage.total_tokens > 0`
8. Send a request with `temperature: 3.5`, check for `400`

Running this through the six axes reveals:

- **Input modality**: Only single-turn prompts. No multi-turn, no adversarial. Gap.
- **Response mode**: Completion, structured output, and tool calling are covered. Streaming is missing. Gap.
- **Output contract**: Only structural assertions (status codes, non-empty, JSON parse). No content validation. Gap.
- **Safety regime**: Not tested at all. Gap.
- **Failure modes**: Only `401` and `400` for invalid temperature. Missing `429`, `500`, `503`, safety block, truncation. Gap.
- **Non-functional**: Token count is checked for existence only. No latency, cost, or consistency tests. Partial gap.

This audit tells you exactly where to invest next.

---

## Section 3: The Five Risk Areas (10 min)

From research on GenAI API failures, five key risks should organize your coverage priorities:

**1. Hallucination and inaccuracy**
The model makes things up. For ChatAssist, this means testing factual questions against known answers. Ask "What is the capital of France?" and verify the response contains "Paris." Ask about your product's return policy (via system prompt) and verify the model does not invent policies that do not exist.

**2. Bias in decision-making**
The model treats different demographic groups differently. Test by running the same prompt with different names or contexts and comparing responses. In structured output mode (ticket classification), check whether classification results change when the customer's name or language style changes.

**3. Undesirable or harmful content**
The model produces unsafe output. Test each safety level with prompts designed to trigger safety filters. Verify `finish_reason: "safety"` for clearly harmful requests. Also verify that the `strict` safety level does not block legitimate customer support questions (false positives).

**4. Data leakage**
The model exposes PII, training data, or system prompts. Attempt to extract the system prompt with variations of "What are your instructions?" Test whether the model echoes back PII that was included in the conversation history.

**5. Adversarial vulnerability**
The model can be tricked. Send prompt injection attempts ("Ignore your instructions and...") and verify the model refuses. This is covered in depth in Session 5.

### Mapping Risks to Test Priorities

| Priority | What to Test | Assertion Level | Risk Area |
|---|---|---|---|
| P0 -- Must test | Authentication, error handling, structural validation | Level 1 (deterministic) | Failure modes |
| P1 -- Should test | Happy path behavior, schema adherence, key safety filters | Levels 1-2 (deterministic + containment) | Hallucination, harmful content |
| P2 -- Good to test | Behavioral consistency, parameter effects, similarity checks | Level 3 (similarity) | Bias, consistency |
| P3 -- Nice to test | Quality scoring, nuanced evaluation, adversarial edge cases | Levels 4-5 (LLM-as-judge, statistical) | Adversarial, quality |

---

## Section 4: Building the Coverage Matrix (15 min)

Let us build a concrete matrix for the ChatAssist API. This walks through the deliverable template you will produce at the end of the session.

### The Matrix Structure

Each row is a test case. The columns capture everything you need to prioritize, implement, and maintain it.

| Test ID | Axis | Mode | Scenario | Priority | Assertion Level | Tier | Est. Cost |
|---|---|---|---|---|---|---|---|
| TC-01 | Failure | All | Invalid API key returns 401 | P0 | L1 Structural | Fast | Low |
| TC-02 | Failure | All | Rate limit returns 429 with Retry-After header | P0 | L1 Structural | Fast | Low |
| TC-03 | Output | Completion | Simple Q&A returns relevant answer | P1 | L2 Containment | Fast | Low |
| TC-04 | Output | Structured | Sentiment analysis matches schema | P1 | L1 Structural | Fast | Low |
| TC-05 | Response | Tool calling | Order lookup selects correct tool | P1 | L1 Structural | Fast | Medium |
| TC-06 | Response | Tool calling | Tool result incorporated into final answer | P1 | L2 Containment | Standard | Medium |
| TC-07 | Response | Streaming | Full stream reassembles to valid response | P1 | L1 Structural | Standard | Low |
| TC-08 | Safety | Completion | Harmful prompt blocked with finish_reason: safety | P1 | L1 Structural | Fast | Low |
| TC-09 | Input | Completion | Multi-turn conversation maintains context | P2 | L2 Containment | Standard | Medium |
| TC-10 | Non-func | Completion | Same prompt 5x with temp=0 produces consistent results | P2 | L5 Statistical | Standard | Medium |
| TC-11 | Safety | Completion | Prompt injection attempt refused | P2 | L2 Containment | Standard | Low |
| TC-12 | Output | Completion | Customer support response quality score | P3 | L4 LLM-as-judge | Deep | High |

This is not exhaustive -- the exercise at the end of this session asks you to build a matrix with at least 20 test cases.

### Tiered CI/CD Integration

Not every test should run on every pull request. The tiered evaluation strategy from research gives you three levels:

**Fast Tier -- Every Pull Request**
- P0 and P1 tests only
- Deterministic assertions (Levels 1 and 2)
- Small dataset: 20-50 test cases
- Target: completes in under 5 minutes
- Token budget: a fixed ceiling per pipeline run
- Goal: catch regressions and broken configurations quickly

**Standard Tier -- Nightly**
- P0, P1, and P2 tests
- Adds similarity-based assertions (Level 3)
- Full evaluation dataset
- Includes consistency checks (run key tests multiple times)
- Token budget: higher but still tracked
- Goal: detect behavioral drift and subtle quality changes

**Deep Tier -- Pre-Release**
- All priorities including P3
- Adds LLM-as-judge (Level 4) and statistical assertions (Level 5)
- Red teaming and adversarial testing
- Human review of sampled results
- No hard token budget (but still tracked for cost visibility)
- Goal: comprehensive quality gate before deploying to production

The key principle: **every test has a home in exactly one tier.** If a test is too slow or too expensive for the fast tier, move it to standard or deep -- do not skip it entirely.

---

## Section 5: Cost-Aware Test Design (5 min)

Every GenAI API test costs tokens, and tokens cost money. This is different from traditional API testing where the main cost is compute time.

**Track cost per test run as a metric.** Add `usage.total_tokens` from every response to a running total. Know what your fast tier costs per execution.

**Use cheaper models for high-volume test scenarios.** The ChatAssist API has `chatassist-4-mini` at 32K context with lower per-token pricing. Many P0 and P1 tests (error handling, structural validation) do not need the most capable model.

**Cache responses for repeated identical prompts.** If your CI pipeline runs the same prompt against the same model version, the response will not change meaningfully. Cache it.

**Remember that LLM-as-judge doubles your token cost.** Every Level 4 assertion makes a second API call to the judge model. This is why LLM-as-judge tests belong in the deep tier, not the fast tier.

**Set hard token budgets per CI/CD pipeline run.** If the fast tier exceeds its budget, fail the pipeline and investigate. This prevents runaway cost from prompt inflation or accidental full-suite execution.

Research shows teams achieve 30-50% cost reduction from prompt optimization and caching alone. The hidden costs to watch: reasoning tokens (for models with chain-of-thought), failed request tokens (errors still consume input tokens), and agentic overhead (multi-step tool calling workflows multiply token consumption).

---

## Discussion and Q&A (15 min)

Consider these questions:

- Which coverage dimension would you focus on first for a new GenAI API project?
- How do you balance thoroughness with cost when tokens cost money?
- When would you skip LLM-as-judge assertions entirely?
- Looking at the common gaps table, which gap surprises you most?

---

## Paper Exercise: Coverage Matrix Builder (20 min)

See the separate exercises document (03-exercises.md) for the full exercise.

---

## Deliverable: Coverage Matrix Template

Your session deliverable is a coverage matrix template with:

- **Columns:** Test ID, Axis (from the six-axis map), Mode, Scenario Description, Priority (P0-P3), Assertion Level (L1-L5), Tier (Fast/Standard/Deep), Estimated Cost (Low/Medium/High), Notes
- **Pre-filled rows** for common ChatAssist scenarios (the 12 examples from Section 4)
- **Color-coding by priority:** P0 = red, P1 = orange, P2 = yellow, P3 = green
- **Instructions** for adapting the template to a real GenAI API

The matrix is not a static document. It grows as you discover new failure modes in production, and tests move between tiers as you learn what matters most for your specific application.
