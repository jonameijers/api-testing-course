# Assertion Selection Guide

> Practical decision guide for choosing the right assertion level when testing GenAI APIs. Based on the five-level Assertion Ladder.

---

## The Assertion Ladder

Use the **lowest level that gives you confidence**. Every test should include Level 1. Add higher levels only where needed.

---

### Level 1: Structural / Format Assertions

**What it checks:** The response has the correct shape, types, and fields.

**Determinism:** Fully deterministic. Same structure every time.

**Stability rating:** HIGH -- rarely produces false failures.

**When to use:**
- Every single test (this is your non-negotiable baseline)
- Validating structured output schema conformance
- Checking error response format
- Verifying token usage fields exist and are numeric

**Examples (ChatAssist API):**
- Response HTTP status is 200
- `response.choices` is a non-empty array
- `choices[0].message.role` equals `"assistant"`
- `choices[0].finish_reason` is one of `["stop", "length", "tool_calls", "safety"]`
- `usage.total_tokens` is a positive integer
- For structured output: parsed `content` JSON matches the provided schema
- For tool calls: `tool_calls[0].function.name` is a string

**Anti-pattern:** Using Level 1 alone when you need to verify the quality or correctness of the response content.

---

### Level 2: Content Containment Assertions

**What it checks:** Specific terms, patterns, or facts appear (or do not appear) in the response.

**Determinism:** Deterministic check, but the content being checked is probabilistic.

**Stability rating:** MEDIUM-HIGH -- stable if the required content is a key fact the model should always include.

**When to use:**
- The response must mention specific required facts ("Paris", "30 days", "$49.99")
- The response must NOT contain prohibited content (PII, competitor names, profanity)
- The response must match a regex pattern (dates, prices, IDs)
- You need keyword coverage ("mentions at least 3 of these 5 topics")

**Examples (ChatAssist API):**
- Response contains "Paris" (capital of France question)
- Response does NOT contain any email address pattern (`/\S+@\S+\.\S+/`)
- Response contains a date in YYYY-MM-DD format
- For tool calls: `arguments` JSON contains `"order_id"` field
- Sentiment analysis response contains one of `["positive", "negative", "neutral", "mixed"]`

**Anti-pattern:** Checking for exact phrases that the model might rephrase. Use containment for facts, not sentences.

---

### Level 3: Similarity-Based Assertions

**What it checks:** The response is semantically close to a reference answer, even if the wording differs.

**Determinism:** Semi-deterministic. The similarity score is computed deterministically from the model's output, but the output varies between runs.

**Stability rating:** MEDIUM -- depends on threshold calibration. Too strict = false failures; too loose = missed regressions.

**When to use:**
- The response can be worded many ways, but the meaning must be consistent
- You have a reference answer to compare against
- Exact text match is too brittle, but keyword search is too loose
- Detecting quality drift over time

**Metrics and typical thresholds:**

| Metric | What It Measures | Typical Threshold |
|--------|-----------------|-------------------|
| Cosine similarity (embeddings) | Semantic closeness of meaning | >= 0.85 |
| ROUGE-1 | Unigram overlap with reference | >= 0.4 |
| ROUGE-L | Longest common subsequence overlap | >= 0.3 |
| BLEU | N-gram precision against reference | >= 0.3 |
| Levenshtein ratio | Character-level similarity | >= 0.7 |

**Examples (ChatAssist API):**
- Math tutor response for "20% of 240" has cosine similarity >= 0.85 to reference answer
- Customer support response about return policy has ROUGE-L >= 0.35 against policy text
- Product description summary maintains semantic similarity across model versions

**Anti-pattern:** Using similarity for structured output (Level 1 is better) or for checking single facts (Level 2 is better). Similarity is for when the overall meaning matters.

---

### Level 4: LLM-as-Judge Assertions

**What it checks:** A separate LLM evaluates whether the response meets qualitative criteria.

**Determinism:** Non-deterministic. The judge itself can give different scores on the same input.

**Stability rating:** LOW-MEDIUM -- requires calibration, self-consistency checks, and human validation.

**When to use:**
- Evaluating subjective quality (helpfulness, tone, professionalism)
- Checking faithfulness to provided context (no hallucination beyond source material)
- Assessing whether the response is appropriate for the audience
- Complex criteria that cannot be reduced to keywords or similarity scores

**Judge prompt templates:**

*Binary classification:*
```
You are evaluating a customer support response.
Does this response accurately describe the return policy without over-promising?
Respond with only "YES" or "NO", then explain your reasoning in one sentence.

[Response to evaluate]
{response}

[Reference policy]
{policy_text}
```

*Rubric-based scoring:*
```
Rate the following response on a scale of 1-5 for each criterion.
- Accuracy (1=incorrect, 5=fully accurate)
- Completeness (1=missing key info, 5=comprehensive)
- Tone (1=rude/robotic, 5=professional and helpful)

Provide your scores as JSON: {"accuracy": N, "completeness": N, "tone": N}
Then explain each score in one sentence.

[Response to evaluate]
{response}
```

**Implementation best practices:**
- Set judge temperature to 0
- Run the judge 3 times per evaluation (self-consistency)
- Calibrate against 50+ human-labeled examples (target Cohen's kappa > 0.8)
- Use few-shot examples (2-3 labeled responses) in the judge prompt
- Split complex criteria into separate judges; combine scores deterministically

**Examples (ChatAssist API):**
- Judge evaluates whether customer support response is helpful AND accurate
- Judge checks if the model's explanation is faithful to the tool call results
- Judge assesses whether the response tone matches the system prompt guidelines

**Anti-pattern:** Using LLM-as-judge for things that can be checked deterministically (schema validation, keyword presence). The judge adds cost and its own non-determinism.

---

### Level 5: Statistical / Aggregate Assertions

**What it checks:** Consistency and quality across multiple runs of the same test.

**Determinism:** Varies. The aggregation is deterministic; the individual runs are not.

**Stability rating:** MEDIUM-HIGH for aggregate metrics. Provides more reliable signal than single-run assertions.

**When to use:**
- Flakiness at lower levels makes single-run assertions unreliable
- You need to quantify consistency (does the model give the same answer most of the time?)
- Tracking quality trends over time (regression detection)
- Validating that a prompt change improves overall performance

**Statistical patterns:**

| Pattern | Implementation | Typical Threshold |
|---------|---------------|-------------------|
| N-of-M pass | Run test 5 times, pass if 4+ pass | 80% pass rate |
| Average score | Run 5 times, compute mean similarity | Mean >= 0.80 |
| Standard deviation | Run 5 times, check consistency | StdDev < 0.15 |
| Trend detection | Compare last 7 daily scores to baseline | No downward trend > 10% |

**Examples (ChatAssist API):**
- "Name a fruit" test passes if 4 out of 5 runs return a valid fruit name
- Customer support quality score averages >= 4.0/5.0 across 10 runs
- Structured output schema compliance is 100% across 20 runs (even though content varies)

**Anti-pattern:** Using statistical assertions when a single deterministic check would suffice. Do not add complexity where it is not needed.

---

## Decision Flowchart

Follow this path to choose the right assertion level for a given requirement.

```
START: What do you need to verify?
|
+-- Is it about response STRUCTURE (schema, types, fields, status codes)?
|   |
|   YES --> Level 1: Structural
|           (Also add Level 1 as baseline for ALL other paths)
|
+-- Is it about the PRESENCE or ABSENCE of specific content?
|   |
|   +-- Can you define exact terms, patterns, or regexes?
|   |   |
|   |   YES --> Level 2: Containment
|   |
|   +-- Is it about the MEANING rather than specific words?
|       |
|       YES --> Level 3: Similarity
|
+-- Is it about QUALITY, APPROPRIATENESS, or complex judgment?
|   |
|   +-- Can you write clear evaluation criteria?
|   |   |
|   |   YES --> Level 4: LLM-as-Judge
|   |           (Remember: this doubles token cost)
|   |
|   +-- Is the criteria too vague for an LLM judge?
|       |
|       YES --> STOP. Clarify requirements before writing the test.
|
+-- Is a single run unreliable for any of the above?
    |
    YES --> Level 5: Statistical
            (Wrap any of the above in N-of-M runs)
```

---

## Layering Guide: Combining Assertion Levels

The most robust tests layer multiple levels. Here are common combinations.

**Basic layering (most tests):**
```
Level 1 (structural)  -- Is the response valid?
  + Level 2 (containment)  -- Does it mention the key facts?
```

**Moderate layering (important tests):**
```
Level 1 (structural)  -- Is the response valid?
  + Level 2 (containment)  -- Does it include/exclude required content?
  + Level 3 (similarity)   -- Is the overall answer close to the reference?
```

**Full layering (critical tests):**
```
Level 1 (structural)  -- Is the response valid?
  + Level 2 (containment)  -- Key facts present, prohibited content absent?
  + Level 4 (LLM-as-judge) -- Is it helpful, accurate, and appropriate?
  + Level 5 (statistical)  -- Does it pass consistently across 5 runs?
```

**Example: Customer support return policy test**
```
Level 1: Response is 200, valid JSON, finish_reason is "stop"
Level 2: Contains "30 days", contains "original condition", does NOT contain "full refund"
Level 4: Judge confirms response is accurate to the policy without over-promising
Level 5: Passes 4 of 5 runs
```

---

## Choosing Thresholds: Practical Guidelines

| Criticality | Similarity Threshold | Judge Score Minimum | Statistical Pass Rate |
|-------------|---------------------|--------------------|-----------------------|
| Safety-critical | >= 0.95 | 5/5 on safety criteria | 5/5 runs |
| Core functionality | >= 0.85 | >= 4/5 | 4/5 runs |
| Standard features | >= 0.75 | >= 3/5 | 3/5 runs |
| Experimental/creative | >= 0.60 | >= 2/5 | 2/5 runs |

**Calibration process:**
1. Run the test 20 times against the current model
2. Manually review outputs and label them pass/fail
3. Set the threshold so that your pass/fail labels align with the automated assertion
4. Re-calibrate quarterly or after any model version change

---

*This guide is a companion to Session 2: The Assertion Ladder. Use it alongside the Coverage Matrix Template to assign assertion levels to test cases.*
