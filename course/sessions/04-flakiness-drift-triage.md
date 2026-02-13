# Session 4: Flakiness, Drift, and Triage

**Duration:** 90 minutes
**Deliverable:** Triage Decision Tree

---

## Learning Objectives

By the end of this session, you will be able to:

1. Distinguish between flakiness, drift, and genuine bugs in GenAI API tests
2. Categorize flakiness by root cause (model-side, infrastructure, test design, evaluation)
3. Apply mitigation strategies for each category of flakiness
4. Use a decision tree to triage test failures
5. Design tests that are resilient to non-determinism without hiding real bugs

---

## Bridge from UI Testing (10 min)

**What you know from UI testing:**
You already know flaky tests. The checkbox animation has not finished when you try to click it. The element is not in the DOM yet. The CDN is slow today. A CSS class was renamed. You have developed instincts for debugging these -- look at timing, look at test isolation, look at the environment. You know the difference between "this test is broken" and "this test found a real bug."

**How this translates to GenAI API testing:**

| UI Flakiness | GenAI API Flakiness |
|---|---|
| Page load timing varies | Model response latency varies |
| Animation not finished before assertion | Streaming not complete before assertion |
| CSS class renamed | Model output format changed |
| Different results on different browsers | Different results from different model versions |
| Element not found in DOM | Expected keyword not found in free-text response |
| Retry with longer wait fixes it | Retry might produce a completely different (but valid) answer |

**Key insight:** Your flakiness debugging instincts transfer directly. The diagnostic approach is the same: *Is this a real bug, an environment issue, or a test design problem?* The root causes are different, but the mental framework is the same.

The critical difference: in UI testing, a retry that produces the same result gives you confidence the failure is real. In GenAI testing, a retry that produces a *different* result does not mean the first result was wrong -- the model is non-deterministic by design.

---

## Section 1: Three Types of Test Failure (10 min)

Every GenAI API test failure falls into one of three categories. The first step in triage is classification.

### Flakiness

**What happened:** The test assertion was too strict for naturally variable output, or a transient condition caused a one-time failure.

**Example:** Your test asserts that the response to "What is your return policy?" contains the exact sentence "We offer a 30-day return window." The model responds with "Our return policy allows returns within 30 days of purchase" -- same fact, different words. The test fails, but the system is working correctly.

**Signal:** The test passes on retry. Results vary from run to run. No pattern in when it fails.

### Drift

**What happened:** The model's behavior changed because the provider updated or replaced the model version.

**Example:** On Monday, the ChatAssist API returns structured, concise answers to product questions. On Wednesday, after a model update, it starts adding emoji and longer explanations. Your containment assertion still finds the key facts, but your similarity assertion fails because the style has changed significantly.

**Signal:** The test fails consistently after a specific date. It worked reliably before. The API contract has not changed, but the output has. Checking the model version in the response (the `model` field) reveals a new version.

### Bug

**What happened:** The application or API has a genuine defect.

**Example:** A code change broke the system prompt configuration, so the model no longer knows about the return policy. Every question about returns gets a generic "I'm not sure about that" response. Or the `lookup_order` tool is misconfigured and always returns an error.

**Signal:** Fails consistently and reproducibly across retries. The error is clear and specific. Not related to wording variation.

### Why Classification Matters

The response to each type is completely different:

| Type | Response |
|---|---|
| Flakiness | Adjust the assertion, add retries, or accept statistical pass criteria |
| Drift | Investigate the model version change, update baselines, consider version pinning |
| Bug | File a defect, fix the root cause, add a regression test |

Misclassifying a bug as flakiness means you soften the assertion and the bug ships to production. Misclassifying flakiness as a bug means the team wastes time investigating a non-issue.

---

## Section 2: The Four Categories of Flakiness (15 min)

Not all flakiness is the same. Each category has different root causes and different mitigations.

### Category 1: Model-Side Flakiness

The model itself produces variable output. This is inherent to how language models work.

**Root causes:**
- Temperature and sampling variation: at any temperature above 0, the model samples from a probability distribution. Different samples, different words.
- Even at `temperature: 0`, floating-point arithmetic and batch processing can produce slight variations.
- Inconsistent refusals: borderline content may be blocked on one run and allowed on the next.
- Load-dependent behavior: some providers route requests to different model instances, which may behave slightly differently.

**ChatAssist example:** Send `"Name a fruit"` with `temperature: 1.5` three times. Get "Mango," then "Starfruit," then "Dragonfruit! It's a tropical favorite." (This is Example 5 from the ChatAssist API spec.) All three are correct -- the test should not fail on any of them.

**Mitigations:**
- Lower temperature for tests that need consistency (`temperature: 0` or `0.1`)
- Use structured output mode to constrain the response format
- Assert on meaning, not wording (use containment or similarity, not exact match)
- Use statistical pass criteria: "passes if 4 of 5 runs meet the threshold"

### Category 2: Infrastructure Flakiness

The API infrastructure causes intermittent failures unrelated to the model's behavior.

**Root causes:**
- Rate limiting: your test suite sends too many requests too fast, triggering `429` errors
- Timeouts: a complex prompt takes longer than your test's timeout allows
- Load balancer variations: requests are routed to different servers with different latency characteristics
- Regional endpoint differences: tests running in different CI/CD environments hit different API regions

**ChatAssist example:** A test suite with 50 tests runs in parallel. Tests 35 through 50 all fail with `429 Rate limit exceeded` because the Free tier only allows 10 requests per minute.

**Mitigations:**
- Retry with exponential backoff and jitter. The jitter (adding a random delay) prevents the "thundering herd" problem where all retries fire at the same instant.
- Set generous timeouts. The ChatAssist API spec shows latency up to 15 seconds for long completions -- a 5-second timeout is too aggressive.
- Control test parallelism. If your rate limit is 60 requests per minute, do not run 60 tests in parallel.
- Use the `Retry-After` header. When ChatAssist returns `429`, the response includes `Retry-After: 12` -- wait exactly that long.
- Implement a circuit breaker: if a provider returns 3 errors in a row, stop sending requests for a cooling period instead of hammering a failing service.

### Category 3: Test Design Flakiness

The test itself is poorly designed for non-deterministic output. This is the most common category for teams transitioning from UI testing, because exact-match instincts do not serve you here.

**Root causes:**
- Overly strict assertions: asserting exact text when the model's output varies
- Hardcoded expected values: expecting one specific valid answer when many valid answers exist
- Phrasing dependence: the test checks for "The capital of France is Paris" but the model says "Paris is the capital of France"
- Missing retry logic: the test treats every transient `500` error as a hard failure

**ChatAssist example:** You write a test that asserts `response.content == "The capital of France is Paris."` The model responds with "Paris is the capital of France." The assertion fails. The model was correct. Your test was wrong.

**Mitigations:**
- Use the assertion ladder. Move to the level that matches your test's actual intent. If you care about correctness, use Level 2 (containment: does it mention "Paris"?) not Level 1 (exact match).
- Write assertions that express what you actually need to verify. "Contains the fact" is almost always better than "matches the sentence."
- Add retry logic for transient errors (429, 500, 503) but *not* for content failures. Retrying a content failure masks real problems.

### Category 4: Evaluation Flakiness

Your assertion mechanism itself is non-deterministic. This only applies to Level 4 (LLM-as-judge) and Level 3 (similarity) assertions.

**Root causes:**
- LLM-as-judge inconsistency: the judge model gives different scores on different runs. A response scores 3/5 one time and 4/5 the next.
- Embedding similarity near threshold boundaries: a response has a similarity score of 0.79 against a threshold of 0.80. Random variation in the embedding causes it to alternate between pass and fail.
- Different judge models disagree: your local judge says "pass" but the CI/CD judge uses a different model and says "fail."

**ChatAssist example:** You set up an LLM-as-judge to evaluate whether customer support responses are "helpful and professional." The judge gives the same response a 4/5 on Monday and a 3/5 on Tuesday. Your pass threshold is 3.5. The test flips between pass and fail.

**Mitigations:**
- Run the judge multiple times (self-consistency check). If you run the judge 3 times and take the majority vote, inconsistency drops significantly.
- Add threshold buffers. If your minimum is 3.5, do not set the threshold to exactly 3.5 -- set it to 3.0 and monitor the distribution.
- Calibrate the judge against human labels. Create a labeled dataset of 50+ responses scored by humans. Run the judge against them and compute agreement (target Cohen's kappa > 0.8). If the judge disagrees with humans too often, the judge prompt needs work.
- Pin the judge model version. The judge itself is an LLM that can drift.

---

## Section 3: Model Drift -- The Silent Test Killer (15 min)

Drift is the failure mode unique to GenAI testing. Traditional APIs do not change behavior unless someone deploys new code. GenAI APIs can change behavior because the provider updated the model, even when your code has not changed and the API contract is the same.

### What Drift Looks Like

**Output format changes.** The model starts adding markdown formatting where it used to return plain text. Your parser breaks because it was not expecting `**bold**` markers in the response.

**Refusal policy updates.** The provider tightened safety filters. Prompts that worked last week now return `finish_reason: "safety"`. Your test suite has 8 new failures that are not bugs in your code.

**Quality shifts.** The model gets measurably better or worse at certain tasks. Similarity scores that averaged 0.88 now average 0.82. Nothing changed on your end.

**Prompt sensitivity changes.** A prompt that reliably triggered tool calling now sometimes produces a direct text response instead, because the model's decision boundary shifted.

**Token counting changes.** The same prompt costs 42 tokens on the old version and 45 on the new version. Your cost tracking tests fail, but the model works fine.

### Real-World Drift Examples

These are real incidents from production GenAI systems (adapted to illustrate the patterns):

**GPT-4o default update (October 2024).** OpenAI updated the default `gpt-4o` alias to point to a newer version. Teams that used the alias instead of pinning to a specific version saw test failures because the model's response style had changed. The API contract was identical -- same endpoint, same parameters, same status codes. But the output was different enough to break containment and similarity assertions.

**GPT-4o structure regression (late 2024).** A specific version of `gpt-4o` stopped reliably following certain output structure instructions. Parsing logic that depended on consistent formatting broke. This was a capability regression that was later fixed, but it caused days of investigation for affected teams.

**GPT-4.5 deprecation (April 2025).** GPT-4.5 was deprecated only months after release, forcing teams to migrate to GPT-4.1. This is not a subtle behavior change -- it is a forced migration on a timeline measured in weeks. Model deprecation timelines in the GenAI space are measured in months, not years.

### Detection Strategies

**Pin to specific model versions.** Use `chatassist-4-2024-08-06` instead of `chatassist-4`. This does not prevent drift -- models still get deprecated -- but it makes drift an explicit event you can plan for instead of a surprise.

**Run evaluations periodically even without code changes.** If your test suite only runs when code changes, you will not detect model drift. Schedule the standard tier to run nightly regardless of commits.

**Maintain a "canary" test suite.** A small set of tests (5-10) that run daily against the *latest* model version alias. When canary tests start failing, you have an early warning that a version update landed.

**Track assertion scores over time.** Store similarity scores and LLM-as-judge scores as time-series data. A gradual decline from 0.88 to 0.82 over two weeks is drift. A sudden drop from 0.88 to 0.45 overnight is a version change.

**Budget for migration work as a regular cost.** Model migration is not a one-time project. It is an ongoing operational cost. Plan for it quarterly, not annually.

---

## Section 4: The Triage Decision Tree (10 min)

This is the session's core deliverable. When a test fails, walk the tree from top to bottom.

```
Test failed
|
+-- Is the error a transient HTTP error? (429, 500, 503, timeout)
|   |
|   +-- YES --> Retry with exponential backoff.
|   |           Still fails after 3 retries?
|   |           |
|   |           +-- YES --> Infrastructure issue.
|   |           |           Check rate limits, quotas, service status.
|   |           |
|   |           +-- NO  --> Transient blip. Test passes. Log and monitor.
|   |
|   +-- NO  --> Continue down the tree.
|
+-- Does the test pass on retry with the same input?
|   |
|   +-- YES --> Likely flakiness.
|   |           Which category?
|   |           - Content varies each run --> Model-side flakiness
|   |           - Score near threshold --> Evaluation flakiness
|   |           Action: Review assertion level. Consider softening,
|   |           statistical pass criteria, or lower temperature.
|   |
|   +-- NO  --> Continue down the tree.
|
+-- Did the model version change recently?
|   |
|   +-- YES --> Likely drift.
|   |           Compare the 'model' field in recent responses
|   |           to historical responses.
|   |           Check provider release notes and deprecation notices.
|   |           Action: Evaluate impact, update baselines or pin version.
|   |
|   +-- NO  --> Continue down the tree.
|
+-- Does the test fail for ALL inputs, or only specific ones?
|   |
|   +-- ALL INPUTS --> Likely a bug.
|   |                  Check: misconfigured API key, broken endpoint,
|   |                  system prompt missing, tool definition error.
|   |                  Action: File defect, investigate root cause.
|   |
|   +-- SPECIFIC INPUTS --> Check if those inputs trigger
|                           safety filters or edge cases.
|                           Test with similar-but-different inputs.
|                           Action: Expand test data, check safety config.
|
+-- Does the test fail consistently and reproducibly?
    |
    +-- YES --> Real bug. File a defect.
    |           Write a minimal reproduction case.
    |           Add it to the regression suite after the fix.
    |
    +-- NO  --> Complex flakiness.
                Layer assertions (L1 + L2 + L3).
                Add statistical pass criteria.
                Investigate with logging and tracing.
```

### Using the Tree Effectively

The tree is designed to be walked from top to bottom. Each branch eliminates a category. By the time you reach the bottom, you have either identified the cause or narrowed it to a complex case that needs deeper investigation.

**Important:** Do not skip straight to "it's flaky" as a default diagnosis. The tree forces you to rule out infrastructure issues and drift before concluding flakiness. This discipline prevents the dangerous pattern of softening assertions to hide real problems.

---

## Section 5: The Continuous Feedback Loop (5 min)

The most important pattern from research on mature GenAI testing teams is the continuous feedback loop:

```
Deploy --> Observe --> Identify failures --> Add to eval suite --> Fix --> Redeploy
                          |                       |
                    (production traces,    (every production failure
                     user feedback,         becomes a regression test)
                     monitoring alerts)
```

**Every production failure becomes a regression test.** When a customer reports that the chatbot gave incorrect return policy information, that exact conversation becomes a test case. When monitoring detects that similarity scores dropped after a model update, the affected prompts become canary tests.

This is the single most important pattern for building a robust GenAI test suite over time. Your initial coverage matrix is a starting point. The feedback loop is how it matures.

### Seven Failure Categories for Production Monitoring

When observing production behavior, classify failures into these categories to feed them into the right part of your test suite:

| Category | Description | Test Suite Destination |
|---|---|---|
| Factual error | Model stated something incorrect | Add as containment assertion (L2) |
| Policy violation | Model contradicted business rules | Add as containment assertion (L2) |
| Safety failure | Model produced harmful content | Add to safety test cases |
| Hallucination | Model fabricated a fact | Add as LLM-as-judge case (L4) |
| Tool misuse | Model called wrong tool or wrong parameters | Add to tool calling tests |
| Performance degradation | Response too slow or too expensive | Add to non-functional tests |
| Format error | Response structure broke downstream systems | Add as structural assertion (L1) |

---

## Discussion and Q&A (15 min)

Consider these questions:

- What is your current instinct when a test fails intermittently? How would that change for GenAI?
- How do you balance "softening assertions" with "catching real bugs"? Where is the line?
- When do you decide a flaky test is not worth fixing and should be deleted?
- Have you experienced anything like "drift" in UI testing? (Hint: think about third-party widget updates or CMS content changes.)

---

## Paper Exercise: Triage Simulation (20 min)

See the separate exercises document (04-exercises.md) for the full exercise.

---

## Deliverable: Triage Decision Tree

Your session deliverable is a visual flowchart suitable for printing and posting on the team's wall:

- **The decision tree** from Section 4 (formatted as a flowchart, not ASCII art)
- **Mitigation action cards** for each flakiness category (model-side, infrastructure, test design, evaluation)
- **Red flags** that distinguish real bugs from flakiness:
  - Consistent failure across all inputs = bug
  - Failure only after a date change = drift
  - Failure with clear error message = bug
  - Failure that varies run to run = flakiness
- **Example failure scenarios** for each path through the tree
- **A maintenance note:** revisit the tree monthly as the team learns more about their specific API's behavior patterns
