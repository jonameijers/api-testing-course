# Coverage Matrix Template

> Blank, vendor-neutral template for planning GenAI API test coverage. Fill in the blanks for your specific API and application.

---

## How to Use This Template

1. Replace `[Your API Name]` with your actual API
2. Fill in each section's blank rows with test cases specific to your application
3. Assign priorities (P0-P3), assertion levels (L1-L5), and CI/CD tiers
4. Use this as a living document -- add rows as you discover new failure modes

---

## Section 1: Test Case Matrix

### Instructions

For each test case, fill in all columns:

| Column | Values | Meaning |
|--------|--------|---------|
| **ID** | T-001, T-002, ... | Unique test identifier |
| **Dimension** | Functional, Safety, Adversarial, Cost, Non-functional | What aspect you are testing |
| **Mode** | Completion, Structured, Tool Calling, Streaming | Which API mode |
| **Scenario** | Free text | What the test does |
| **Priority** | P0, P1, P2, P3 | How important (see Priority Guide below) |
| **Assertion Level** | L1, L2, L3, L4, L5 | Which assertion levels to apply (see Assertion Guide) |
| **Tier** | Fast, Standard, Deep | When this test runs in CI/CD |
| **Est. Cost** | Low, Medium, High | Relative token cost per execution |
| **Notes** | Free text | Special considerations |

---

### Matrix: Input Modality and Response Mode

_Fill in test cases for each combination of input type and response mode your application uses._

| ID | Dimension | Mode | Scenario | Priority | Assertion | Tier | Cost | Notes |
|----|-----------|------|----------|----------|-----------|------|------|-------|
| T-001 | Functional | Completion | _Simple single-turn Q&A_ | _____ | _____ | _____ | Low | _Baseline happy path_ |
| T-002 | Functional | Completion | _Multi-turn conversation_ | _____ | _____ | _____ | Med | _Test context retention_ |
| T-003 | Functional | Structured | _Schema-valid response_ | _____ | _____ | _____ | Low | _Use strict: true_ |
| T-004 | Functional | Structured | _Schema with nested objects_ | _____ | _____ | _____ | Low | _____ |
| T-005 | Functional | Tool Calling | _Correct tool selection_ | _____ | _____ | _____ | Med | _Single tool call_ |
| T-006 | Functional | Tool Calling | _Multi-step tool flow_ | _____ | _____ | _____ | High | _Tool result -> final answer_ |
| T-007 | Functional | Streaming | _Complete stream received_ | _____ | _____ | _____ | Med | _Concatenate all chunks_ |
| T-008 | Functional | Streaming | _Mid-stream error handling_ | _____ | _____ | _____ | Med | _____ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |

---

### Matrix: Output Contract Verification

_Fill in test cases for response structure, format, and content requirements._

| ID | Dimension | Mode | Scenario | Priority | Assertion | Tier | Cost | Notes |
|----|-----------|------|----------|----------|-----------|------|------|-------|
| T-020 | Functional | _Any_ | _Response is valid JSON_ | P0 | L1 | Fast | Low | _Every test includes this_ |
| T-021 | Functional | _Any_ | _Required fields present_ | P0 | L1 | Fast | Low | _choices, message, role_ |
| T-022 | Functional | _Any_ | _finish_reason is valid enum_ | P0 | L1 | Fast | Low | _____ |
| T-023 | Functional | _Any_ | _usage.total_tokens > 0_ | P1 | L1 | Fast | Low | _____ |
| T-024 | Functional | Structured | _Parsed content matches schema_ | P0 | L1 | Fast | Low | _JSON parse content field_ |
| T-025 | Functional | _Any_ | _Response contains required facts_ | P1 | L2 | Fast | Low | _____ |
| T-026 | Functional | _Any_ | _Response does not contain PII_ | P0 | L2 | Fast | Low | _Regex for email, phone, SSN_ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |

---

### Matrix: Safety Regime

_Fill in test cases for safety filters, content moderation, and responsible AI._

| ID | Dimension | Mode | Scenario | Priority | Assertion | Tier | Cost | Notes |
|----|-----------|------|----------|----------|-----------|------|------|-------|
| T-040 | Safety | Completion | _Safety filter blocks harmful content_ | P0 | L1 | Fast | Low | _finish_reason == "safety"_ |
| T-041 | Safety | Completion | _Strict mode blocks borderline content_ | P1 | L1 | Standard | Low | _____ |
| T-042 | Safety | Completion | _Minimal mode allows borderline content_ | P2 | L1+L2 | Standard | Low | _____ |
| T-043 | Safety | _Any_ | _Response doesn't contain hate speech_ | P0 | L2+L4 | Standard | Med | _Keyword + LLM-as-judge_ |
| T-044 | Safety | _Any_ | _Response doesn't generate PII_ | P0 | L2 | Fast | Low | _____ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |

---

### Matrix: Failure Modes and Error Handling

_Fill in test cases for every documented error path._

| ID | Dimension | Mode | Scenario | Priority | Assertion | Tier | Cost | Notes |
|----|-----------|------|----------|----------|-----------|------|------|-------|
| T-060 | Functional | _Any_ | _401 with invalid API key_ | P0 | L1 | Fast | Low | _No tokens consumed_ |
| T-061 | Functional | _Any_ | _400 with invalid temperature_ | P0 | L1 | Fast | Low | _____ |
| T-062 | Functional | _Any_ | _400 with context window exceeded_ | P1 | L1 | Fast | Low | _____ |
| T-063 | Functional | _Any_ | _429 rate limit with Retry-After_ | P0 | L1 | Fast | Low | _Check retry header_ |
| T-064 | Functional | _Any_ | _429 token quota exceeded_ | P1 | L1 | Standard | Low | _____ |
| T-065 | Functional | _Any_ | _500 internal server error_ | P1 | L1 | Standard | Low | _Verify retry logic_ |
| T-066 | Functional | _Any_ | _503 model overloaded_ | P1 | L1 | Standard | Low | _____ |
| T-067 | Functional | Completion | _finish_reason "length" (truncated)_ | P1 | L1+L2 | Fast | Low | _max_tokens too low_ |
| T-068 | Functional | Structured | _Invalid schema returns 400_ | P1 | L1 | Fast | Low | _____ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |

---

### Matrix: Adversarial and Security

_Fill in test cases for prompt injection, data leakage, and abuse scenarios._

| ID | Dimension | Mode | Scenario | Priority | Assertion | Tier | Cost | Notes |
|----|-----------|------|----------|----------|-----------|------|------|-------|
| T-080 | Adversarial | Completion | _Direct prompt injection (ignore instructions)_ | P1 | L1+L2 | Standard | Low | _____ |
| T-081 | Adversarial | Completion | _System prompt extraction attempt_ | P1 | L2 | Standard | Low | _Assert system prompt text absent_ |
| T-082 | Adversarial | Tool Calling | _Model asked to call unauthorized tool_ | P1 | L1 | Standard | Med | _____ |
| T-083 | Adversarial | _Any_ | _PII extraction attempt_ | P1 | L2 | Standard | Low | _____ |
| T-084 | Adversarial | _Any_ | _Encoding tricks (base64 injection)_ | P2 | L2 | Deep | Low | _____ |
| T-085 | Adversarial | _Any_ | _Language switching injection_ | P2 | L2 | Deep | Low | _____ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |

---

### Matrix: Non-Functional Requirements

_Fill in test cases for performance, cost, and consistency._

| ID | Dimension | Mode | Scenario | Priority | Assertion | Tier | Cost | Notes |
|----|-----------|------|----------|----------|-----------|------|------|-------|
| T-100 | Non-functional | _Any_ | _Response latency within timeout_ | P1 | L1 | Fast | Low | _Set generous timeouts_ |
| T-101 | Non-functional | Streaming | _Time to first token < threshold_ | P2 | L1 | Standard | Med | _____ |
| T-102 | Non-functional | _Any_ | _Token usage within budget_ | P1 | L1 | Fast | Low | _Check usage.total_tokens_ |
| T-103 | Non-functional | _Any_ | _Repeat 5x: consistency check_ | P2 | L5 | Deep | High | _Same prompt, measure variance_ |
| T-104 | Non-functional | _Any_ | _Model version matches expected_ | P1 | L1 | Fast | Low | _Detect silent version changes_ |
| _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ | _____ |

---

## Section 2: Priority Guide

| Priority | Meaning | Criteria | Run Frequency |
|----------|---------|----------|---------------|
| **P0** | Must test | Failure here means the system is broken. Auth, structural validation, critical safety. | Every PR (Fast tier) |
| **P1** | Should test | Failure here means a key feature is degraded. Happy paths, error handling, basic safety. | Every PR + nightly |
| **P2** | Good to test | Failure here means quality may be impacted. Consistency, similarity, parameter effects. | Nightly (Standard tier) |
| **P3** | Nice to test | Failure here provides deeper insight. Quality scoring, adversarial edge cases, trend analysis. | Pre-release (Deep tier) |

---

## Section 3: Tiered CI/CD Model

### Fast Tier (Every Pull Request)

**Purpose:** Quick feedback. Block merges that break fundamentals.

**Contents:**
- All P0 test cases
- Selected P1 test cases (happy paths, basic errors)
- Only Level 1 and Level 2 assertions
- Small dataset: 20-50 test cases

**Budget:**
- Runtime target: < 5 minutes
- Token budget: _____________ tokens per run
- Estimated cost: $_____________  per run

**Test cases in this tier:** _(list your Fast-tier test IDs)_
```
[ ]  _____________________________________
[ ]  _____________________________________
[ ]  _____________________________________
```

---

### Standard Tier (Nightly)

**Purpose:** Thorough validation. Catch regressions and quality drift.

**Contents:**
- All P0 + P1 test cases
- Selected P2 test cases
- Level 1 through Level 3 assertions (add similarity checks)
- Moderate dataset: 50-200 test cases

**Budget:**
- Runtime target: < 30 minutes
- Token budget: _____________ tokens per run
- Estimated cost: $_____________  per run

**Test cases in this tier:** _(list your Standard-tier test IDs)_
```
[ ]  _____________________________________
[ ]  _____________________________________
[ ]  _____________________________________
```

---

### Deep Tier (Pre-Release / Weekly)

**Purpose:** Comprehensive evaluation. Validate quality, safety, and adversarial resilience.

**Contents:**
- All priority levels (P0 through P3)
- All assertion levels including Level 4 (LLM-as-judge) and Level 5 (statistical)
- Red teaming and adversarial test cases
- Full dataset: 200+ test cases
- Human review for sampled outputs

**Budget:**
- Runtime target: < 2 hours
- Token budget: _____________ tokens per run
- Estimated cost: $_____________  per run

**Test cases in this tier:** _(list your Deep-tier test IDs)_
```
[ ]  _____________________________________
[ ]  _____________________________________
[ ]  _____________________________________
```

---

## Section 4: Coverage Summary Scorecard

Fill this in after completing the matrix to visualize your coverage.

### By Mode

| Mode | P0 Count | P1 Count | P2 Count | P3 Count | Total |
|------|----------|----------|----------|----------|-------|
| Completion | _____ | _____ | _____ | _____ | _____ |
| Structured Output | _____ | _____ | _____ | _____ | _____ |
| Tool Calling | _____ | _____ | _____ | _____ | _____ |
| Streaming | _____ | _____ | _____ | _____ | _____ |
| **Total** | _____ | _____ | _____ | _____ | _____ |

### By Dimension

| Dimension | Fast Tier | Standard Tier | Deep Tier | Total |
|-----------|-----------|---------------|-----------|-------|
| Functional | _____ | _____ | _____ | _____ |
| Safety | _____ | _____ | _____ | _____ |
| Adversarial | _____ | _____ | _____ | _____ |
| Cost | _____ | _____ | _____ | _____ |
| Non-functional | _____ | _____ | _____ | _____ |
| **Total** | _____ | _____ | _____ | _____ |

### By Assertion Level

| Assertion Level | Test Count | % of Total |
|----------------|-----------|------------|
| L1 only | _____ | _____% |
| L1 + L2 | _____ | _____% |
| L1 + L2 + L3 | _____ | _____% |
| Includes L4 | _____ | _____% |
| Includes L5 | _____ | _____% |

---

## Section 5: Coverage Gaps Checklist

Review this list after filling in the matrix. Check each box to confirm coverage.

### Input Coverage
- [ ] Single-turn messages
- [ ] Multi-turn conversations (3+ turns)
- [ ] Long prompts (near context window limit)
- [ ] Empty or minimal prompts
- [ ] Prompts with special characters and Unicode
- [ ] Prompts in multiple languages (if applicable)
- [ ] ____________________________________________

### Parameter Coverage
- [ ] Default parameters (no overrides)
- [ ] temperature = 0 (near-deterministic)
- [ ] temperature = 2.0 (maximum randomness)
- [ ] max_tokens = 1 (extreme truncation)
- [ ] max_tokens = model maximum
- [ ] All supported model versions
- [ ] ____________________________________________

### Error Path Coverage
- [ ] Invalid authentication (401)
- [ ] Permission denied (403)
- [ ] Rate limit exceeded (429)
- [ ] Token quota exceeded (429)
- [ ] Server error (500)
- [ ] Model overloaded (503)
- [ ] Invalid parameter values (400)
- [ ] Context window exceeded (400)
- [ ] Invalid JSON in request (400)
- [ ] ____________________________________________

### Safety Coverage
- [ ] Each configured safety category tested
- [ ] Each safety level tested (strict, standard, minimal)
- [ ] Borderline content near filter threshold
- [ ] Content that should pass all levels
- [ ] ____________________________________________

### Adversarial Coverage
- [ ] Direct prompt injection (at least 3 variants)
- [ ] Indirect prompt injection (if RAG or tools are used)
- [ ] System prompt extraction attempts
- [ ] PII extraction attempts
- [ ] Encoding-based injection (base64, Unicode tricks)
- [ ] ____________________________________________

---

## Adapting This Template

**For a different GenAI API:**
1. Replace mode names with your API's modes (e.g., "image generation" for multimodal APIs)
2. Update error codes to match your API's error catalog
3. Adjust safety categories to your provider's moderation system
4. Add modality-specific dimensions (vision accuracy, audio WER) if applicable

**For a RAG application, add:**
- Retrieval quality test cases (precision, recall)
- Context poisoning and document injection test cases
- Empty retrieval handling
- Conflicting context scenarios

**For an agent/tool-calling application, add:**
- Tool selection correctness for each available tool
- Multi-step workflow completion
- Infinite loop detection
- Agent privilege boundary testing
- Cost tracking for multi-step agent workflows

---

*This template is a companion to Session 3: Coverage Model. Use it alongside the Assertion Selection Guide and the Triage Decision Tree.*
