# Failure Triage Decision Tree

> Printable decision tree for classifying GenAI API test failures. Walk through the questions from top to bottom. Each path leads to a classification and recommended action.

---

## The Seven Failure Categories

Before using the decision tree, know the categories you are sorting into:

| # | Category | Description | Urgency |
|---|----------|-------------|---------|
| 1 | **Infrastructure Failure** | Server errors, timeouts, rate limiting -- the API is not working | High if persistent |
| 2 | **Authentication / Config Failure** | Bad API key, wrong endpoint, misconfigured parameters | High -- fix immediately |
| 3 | **Model-Side Flakiness** | Model gives different (but valid) answers due to sampling randomness | Low -- adjust assertions |
| 4 | **Test Design Flakiness** | Assertions too strict for naturally variable output | Low -- fix the test |
| 5 | **Evaluation Flakiness** | LLM-as-judge or similarity score inconsistency | Medium -- recalibrate |
| 6 | **Model Drift / Regression** | Model version change caused behavior shift | High -- investigate |
| 7 | **Genuine Bug** | The application or API is truly broken | High -- file defect |

---

## Primary Decision Tree

Start here for every test failure.

```
TEST FAILED
    |
    v
Q1: Is the failure an HTTP error (4xx, 5xx, timeout)?
    |
    +-- YES --> Go to BRANCH A: HTTP Error Triage
    |
    +-- NO (got 200, but assertion failed) --> Go to Q2
    |
    v
Q2: Does the test pass when you retry immediately (same input)?
    |
    +-- YES (passes on retry) --> Go to BRANCH B: Intermittent Failure Triage
    |
    +-- NO (fails consistently) --> Go to Q3
    |
    v
Q3: Did the model version change since the last passing run?
    |
    +-- YES --> Go to BRANCH C: Drift Triage
    |
    +-- DON'T KNOW --> Check response.model field; compare to last known good run
    |
    +-- NO (same model version) --> Go to Q4
    |
    v
Q4: Does the failure happen for ALL test inputs or only SPECIFIC ones?
    |
    +-- ALL inputs fail --> Go to BRANCH D: Systematic Failure
    |
    +-- SPECIFIC inputs fail --> Go to BRANCH E: Input-Specific Failure
```

---

## BRANCH A: HTTP Error Triage

_The API returned a non-200 status code or the request timed out._

```
What is the status code?
    |
    +-- 401 Unauthorized
    |       |
    |       v
    |   Classification: AUTHENTICATION / CONFIG FAILURE (#2)
    |   Action: Check API key. Is it expired? Is it in the right environment variable?
    |           Has the key been rotated? Check CI/CD secrets configuration.
    |
    +-- 400 Bad Request
    |       |
    |       v
    |   Read the error.message and error.param fields.
    |       |
    |       +-- "temperature must be between..." or similar parameter error
    |       |       --> Classification: AUTHENTICATION / CONFIG FAILURE (#2)
    |       |       --> Action: Fix the parameter value in the test.
    |       |
    |       +-- "context window exceeded..."
    |       |       --> Classification: TEST DESIGN FLAKINESS (#4)
    |       |       --> Action: Reduce prompt size or use a model with larger window.
    |       |
    |       +-- "Invalid JSON Schema..."
    |               --> Classification: TEST DESIGN FLAKINESS (#4)
    |               --> Action: Fix the schema definition.
    |
    +-- 429 Too Many Requests
    |       |
    |       v
    |   Read the error.type field.
    |       |
    |       +-- "rate_limit_error"
    |       |       --> Classification: INFRASTRUCTURE FAILURE (#1)
    |       |       --> Action: Add retry with exponential backoff and jitter.
    |       |           Check if other tests are consuming the rate limit.
    |       |           Consider running tests sequentially or with rate limiting.
    |       |
    |       +-- "quota_exceeded"
    |               --> Classification: INFRASTRUCTURE FAILURE (#1)
    |               --> Action: Wait for quota reset. Review test suite token consumption.
    |                   Consider using cheaper model for high-volume tests.
    |
    +-- 500 Internal Server Error
    |       |
    |       v
    |   Does it happen on retry?
    |       +-- NO --> Classification: INFRASTRUCTURE FAILURE (#1) (transient)
    |       |         Action: Add retry logic. Log for monitoring. Not actionable.
    |       +-- YES --> Classification: GENUINE BUG (#7) on the API provider side
    |                   Action: Check provider status page. File support ticket if persistent.
    |
    +-- 503 Service Unavailable
    |       |
    |       v
    |   Classification: INFRASTRUCTURE FAILURE (#1)
    |   Action: Retry with backoff. Check provider status. Consider fallback model.
    |
    +-- Timeout (no response received)
            |
            v
        Is the prompt unusually long or complex?
            +-- YES --> Classification: TEST DESIGN FLAKINESS (#4)
            |           Action: Increase timeout. Consider reducing prompt length.
            +-- NO  --> Classification: INFRASTRUCTURE FAILURE (#1)
                        Action: Retry with backoff. Check network connectivity.
```

---

## BRANCH B: Intermittent Failure Triage

_The test passes on retry. Something is non-deterministic._

```
What type of assertion failed?
    |
    +-- Structural (Level 1) assertion
    |       |
    |       v
    |   This should NOT be intermittent. Investigate deeper.
    |       |
    |       +-- Was it a streaming test?
    |       |       +-- YES --> Possible chunk ordering or connection issue
    |       |       |           Classification: INFRASTRUCTURE FAILURE (#1)
    |       |       +-- NO  --> Possible race condition in test code
    |       |                   Classification: TEST DESIGN FLAKINESS (#4)
    |
    +-- Containment (Level 2) assertion
    |       |
    |       v
    |   Is the required term a key fact (e.g., "Paris" for capital of France)?
    |       +-- YES --> The model is occasionally omitting a critical fact.
    |       |           Classification: MODEL-SIDE FLAKINESS (#3)
    |       |           Action: Lower temperature. Add the fact to system prompt.
    |       |                   Consider statistical pass (4 of 5 runs).
    |       +-- NO  --> The assertion checks for specific phrasing, not facts.
    |                   Classification: TEST DESIGN FLAKINESS (#4)
    |                   Action: Broaden the assertion. Check for meaning, not words.
    |
    +-- Similarity (Level 3) assertion
    |       |
    |       v
    |   Is the score close to the threshold (within 0.05)?
    |       +-- YES --> Classification: TEST DESIGN FLAKINESS (#4)
    |       |           Action: Widen threshold slightly. Run 5x, check distribution.
    |       +-- NO  --> Score is well below threshold on some runs.
    |                   Classification: MODEL-SIDE FLAKINESS (#3)
    |                   Action: Lower temperature. Review prompt for ambiguity.
    |
    +-- LLM-as-Judge (Level 4) assertion
    |       |
    |       v
    |   Run the judge 3 times on the same response. Does it give the same score?
    |       +-- NO  --> Classification: EVALUATION FLAKINESS (#5)
    |       |           Action: Set judge temperature to 0. Add few-shot examples.
    |       |                   Simplify judge criteria. Consider switching to Level 2/3.
    |       +-- YES --> Judge is consistent, but the response varies.
    |                   Classification: MODEL-SIDE FLAKINESS (#3)
    |                   Action: Use statistical pass criteria (N of M runs).
    |
    +-- Statistical (Level 5) assertion
            |
            v
        The aggregate metric missed the threshold.
        Check individual run scores. Is there an outlier?
            +-- YES (1 bad run out of 5) --> Probably acceptable variance.
            |       Classification: MODEL-SIDE FLAKINESS (#3)
            |       Action: Increase N (more runs) or lower threshold slightly.
            +-- NO (multiple bad runs) --> Quality issue.
                    Classification: MODEL DRIFT / REGRESSION (#6) -- go to Branch C.
```

---

## BRANCH C: Drift Triage

_The model version changed and behavior shifted._

```
Compare the response.model from failing runs to the last known passing run.
    |
    +-- Model version IS different
    |       |
    |       v
    |   What kind of behavior change do you see?
    |       |
    |       +-- Output FORMAT changed (e.g., markdown added, structure different)
    |       |       Classification: MODEL DRIFT (#6)
    |       |       Action: Update parsing logic. Add format-resilient assertions.
    |       |               Consider using structured output mode to lock format.
    |       |
    |       +-- Output QUALITY changed (worse answers, more hallucination)
    |       |       Classification: MODEL DRIFT (#6)
    |       |       Action: Document the regression. Pin to previous model version.
    |       |               Run full evaluation suite on new vs. old version.
    |       |               Report to provider if significant.
    |       |
    |       +-- REFUSAL behavior changed (model now refuses previously OK prompts)
    |       |       Classification: MODEL DRIFT (#6)
    |       |       Action: Check if the prompt genuinely crosses a policy line.
    |       |               If not, rephrase or pin to previous version.
    |       |
    |       +-- TOKEN COSTS changed (same prompt uses more/fewer tokens)
    |               Classification: MODEL DRIFT (#6)
    |               Action: Update token budget estimates. Review cost thresholds.
    |
    +-- Model version is the SAME
            |
            v
        Check if the provider made a silent update (same alias, different behavior).
        Log response.model values over time to detect this.
            +-- Behavior DID change --> Classification: MODEL DRIFT (#6)
            |       Action: Pin to a dated version (e.g., chatassist-4-2024-08-06).
            +-- Behavior did NOT change --> Go back to Q4 in the primary tree.
```

---

## BRANCH D: Systematic Failure

_ALL test cases are failing, not just specific ones._

```
Are ALL tests failing, or all tests of a specific type?
    |
    +-- ALL tests across the board
    |       |
    |       v
    |   Check authentication and connectivity first.
    |       +-- API key valid? --> If NO: Classification: AUTH/CONFIG FAILURE (#2)
    |       +-- API reachable? --> If NO: Classification: INFRASTRUCTURE FAILURE (#1)
    |       +-- Provider status page shows outage? --> INFRASTRUCTURE FAILURE (#1)
    |       +-- None of the above --> Classification: GENUINE BUG (#7)
    |               Action: Check for recent deployment or config changes.
    |
    +-- All tests of ONE MODE are failing (e.g., all structured output tests)
    |       |
    |       v
    |   Classification: GENUINE BUG (#7) or AUTH/CONFIG FAILURE (#2)
    |   Action: Check if the mode configuration changed. Check API permissions.
    |           Verify request body structure for that mode.
    |
    +-- All tests with a SPECIFIC assertion level are failing
            |
            v
        Classification: TEST DESIGN FLAKINESS (#4) or EVALUATION FLAKINESS (#5)
        Action: Review the assertion threshold. Check if a dependency changed
                (embedding model, judge model, evaluation library version).
```

---

## BRANCH E: Input-Specific Failure

_Only certain test inputs cause failures._

```
What is special about the failing inputs?
    |
    +-- They contain adversarial/sensitive content
    |       |
    |       v
    |   Is the test expecting the model to BLOCK the content?
    |       +-- YES, and the model is NOT blocking --> Classification: GENUINE BUG (#7)
    |       |       Action: Check safety filter configuration. File defect.
    |       +-- YES, and the model IS blocking (but assertion is wrong)
    |       |       --> Classification: TEST DESIGN FLAKINESS (#4)
    |       +-- NO, the test expects the model to handle it normally
    |               --> The model's safety filters may have changed.
    |               Classification: MODEL DRIFT (#6)
    |               Action: Review the input. Adjust if borderline.
    |
    +-- They are edge cases (very long, very short, special characters)
    |       |
    |       v
    |   Was this a known edge case that previously passed?
    |       +-- YES --> Classification: MODEL DRIFT (#6) or GENUINE BUG (#7)
    |       +-- NO  --> Classification: TEST DESIGN FLAKINESS (#4)
    |               Action: Ensure the test expectation is realistic for the input.
    |
    +-- They involve specific tools or functions
    |       |
    |       v
    |   Is the model calling the WRONG tool?
    |       +-- YES --> Classification: GENUINE BUG (#7) or MODEL DRIFT (#6)
    |       |           Action: Check if tool descriptions are clear enough.
    |       +-- NO, right tool but wrong arguments
    |               --> Classification: MODEL-SIDE FLAKINESS (#3)
    |               Action: Validate argument types. Lower temperature.
    |
    +-- No obvious pattern
            |
            v
        Run the failing inputs 5 times each. What is the pass rate?
            +-- > 80% pass rate --> Classification: MODEL-SIDE FLAKINESS (#3)
            |       Action: Add statistical pass criteria.
            +-- < 50% pass rate --> Classification: GENUINE BUG (#7)
                    Action: Investigate the specific inputs. Check for patterns.
```

---

## The Flake vs. Regression Rubric

Use this rubric when it is not obvious whether a failure is flakiness or a real regression.

| Signal | Points to FLAKINESS | Points to REGRESSION |
|--------|--------------------|--------------------|
| **Retry behavior** | Passes on some retries | Fails on every retry |
| **Scope** | One or a few tests | Many tests or a category of tests |
| **Timing** | Random; no correlation with events | Started after a specific date or deployment |
| **Model version** | Same version as before | Different version (check `response.model`) |
| **Score proximity** | Score is close to threshold | Score dropped significantly |
| **Historical trend** | Occasional failures in the past too | No failures before a specific point |
| **Other environments** | Only fails in CI, not locally (or vice versa) | Fails everywhere |

**Scoring:**
- 5+ signals pointing to flakiness --> Treat as flakiness. Adjust assertions or add retries.
- 5+ signals pointing to regression --> Treat as regression. Investigate root cause.
- Mixed signals --> Collect more data. Run 10x. Compare to historical baseline.

---

## Action Cards by Category

### Infrastructure Failure (#1)
- [ ] Check provider status page
- [ ] Verify network connectivity from test environment
- [ ] Review rate limit usage across the test suite
- [ ] Ensure retry logic with exponential backoff + jitter is in place
- [ ] Consider adding circuit breaker for extended outages
- [ ] Log `Retry-After` and `X-RateLimit-Remaining` headers for debugging

### Authentication / Config Failure (#2)
- [ ] Verify API key is present and not expired
- [ ] Check CI/CD secrets are correctly configured
- [ ] Confirm endpoint URL is correct
- [ ] Verify model ID is valid and accessible with your plan
- [ ] Check for recent key rotations

### Model-Side Flakiness (#3)
- [ ] Lower temperature (try 0.0 for maximum consistency)
- [ ] Add system prompt instructions for consistent formatting
- [ ] Use structured output mode where possible
- [ ] Switch from exact assertions to containment or similarity
- [ ] Add statistical pass criteria (N of M runs)

### Test Design Flakiness (#4)
- [ ] Move up the assertion ladder (exact -> containment -> similarity)
- [ ] Widen similarity thresholds (is your threshold too tight?)
- [ ] Use negative assertions (what should NOT appear) alongside positive
- [ ] Increase test timeouts for long completions
- [ ] Reduce prompt ambiguity (clearer instructions = more consistent output)

### Evaluation Flakiness (#5)
- [ ] Set judge model temperature to 0
- [ ] Run judge 3x per evaluation (self-consistency check)
- [ ] Add few-shot examples to judge prompt
- [ ] Simplify evaluation criteria (split complex criteria into separate judges)
- [ ] Calibrate against human-labeled examples (target kappa > 0.8)

### Model Drift (#6)
- [ ] Log and compare `response.model` across runs
- [ ] Run full evaluation suite on new model version
- [ ] Pin to specific model version in test configuration
- [ ] Update assertions and thresholds if drift is acceptable
- [ ] Maintain a "canary" test suite that runs daily for early detection
- [ ] Check provider deprecation announcements and timelines

### Genuine Bug (#7)
- [ ] Document: input, expected output, actual output, model version, timestamp
- [ ] Reproduce consistently
- [ ] Determine if the bug is in your application, the prompt, or the API provider
- [ ] File a defect with reproduction steps
- [ ] Add this failure as a permanent regression test case

---

## Maintaining This Tree

This decision tree should evolve as your team learns more about your specific API and application.

- [ ] Review the tree monthly: are there paths that never get used?
- [ ] Add new branches when you encounter failure modes not covered here
- [ ] Track which categories are most common -- invest in prevention for the top category
- [ ] Share findings from triage sessions with the team to build collective knowledge
- [ ] Convert every production failure into a new test case (the continuous feedback loop)

---

*This decision tree is a companion to Session 4: Flakiness, Drift, and Triage. Print it and post it near your team's monitor wall.*
