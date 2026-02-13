# Session 2: The Assertion Ladder

**Duration:** 90 minutes
**Deliverable:** Assertion Strength Guide

## Learning Objectives

By the end of this session, you will be able to:

1. Name and describe the five levels of the assertion ladder
2. Choose the appropriate assertion level for a given test scenario
3. Write structural, containment, similarity, and LLM-as-judge assertion specifications (on paper)
4. Explain when LLM-as-judge is appropriate and what its risks are
5. Apply the principle: "assert at the lowest level that gives you confidence"

---

## Bridge from UI Testing (10 min)

You already use a range of assertion strengths in UI testing:

```
Exact text match:     expect(element.text).toBe("Add to Cart")
Partial match:        expect(element.text).toContain("Cart")
Regex match:          expect(element.text).toMatch(/\$\d+\.\d{2}/)
Visual comparison:    screenshot diff with a tolerance threshold
Presence check:       expect(element).toBeVisible()
```

You do not use the strongest assertion every time. You match the assertion to the situation: exact match for a button label that must not change, partial match for a page that has dynamic content, visual diff for a layout check.

GenAI API testing has the same ladder, but extended:

| UI Testing Assertion | GenAI API Equivalent |
|---|---|
| Exact text match | Rarely useful (output varies) |
| Partial match / containment | "Does the response mention the key fact?" |
| Regex | "Does the response contain a price in the right format?" |
| Visual comparison (with tolerance) | **Semantic similarity** (cosine distance between embeddings) |
| Presence check | **Structural validation** (is it valid JSON? does it have required fields?) |
| *No UI equivalent* | **LLM-as-judge** -- ask another model to grade the response |

**Key insight:** You already know how to choose assertion strength. The difference in GenAI testing is that the ladder extends upward with two new levels (similarity-based and LLM-as-judge), and the sweet spot shifts -- you will use exact match less and semantic comparison more.

---

## Section 1: The Assertion Ladder -- Overview (10 min)

Here is the five-level framework. Each level trades determinism for expressive power:

| Level | Name | Determinism | When to Use |
|-------|------|-------------|-------------|
| 1 | Structural / Format | Deterministic | Always -- as a baseline |
| 2 | Content Containment | Deterministic | When key facts or terms must appear |
| 3 | Similarity-Based | Semi-deterministic | When meaning matters more than wording |
| 4 | LLM-as-Judge | Non-deterministic | When quality or appropriateness must be assessed |
| 5 | Statistical / Aggregate | Varies | When consistency across runs matters |

**The guiding principle:** Assert at the lowest level that gives you confidence. Level 1 is cheap, fast, and reliable. Level 4 is powerful but expensive and itself non-deterministic. Use the strongest tool only when weaker tools are insufficient.

**How mature teams use the ladder:** Every test includes Level 1. Most tests include Level 2. Levels 3 through 5 are layered on where needed. You rarely use just one level -- you combine them.

---

## Section 2: Level 1 -- Structural Assertions (10 min)

The foundation layer. Always present. Zero ambiguity. These assertions verify the *shape* of the response, not its content.

### What to Check

- Response status code is 200
- Response body is valid JSON
- `choices` array has at least one element
- `choices[0].message.role` is `"assistant"`
- `choices[0].finish_reason` is one of the expected values (`"stop"`, `"length"`, `"tool_calls"`)
- `usage.total_tokens` is a positive integer
- For structured output: the `content` field parses as valid JSON matching the provided schema

### Pseudo-code Example

```
test "ChatAssist response has valid structure":
    response = send_chat_request(prompt: "What is the capital of France?")

    assert response.status_code == 200
    assert response.body is valid JSON
    assert response.body.choices is a non-empty array
    assert response.body.choices[0].message.role == "assistant"
    assert response.body.choices[0].message.content is a non-empty string
    assert response.body.choices[0].finish_reason in ["stop", "length"]
    assert response.body.usage.total_tokens > 0
    assert response.body.usage.prompt_tokens > 0
    assert response.body.usage.completion_tokens > 0
```

### Structured Output Makes Level 1 Powerful

When you use Structured Output with `strict: true`, Level 1 assertions become even more valuable. Consider the sentiment analysis example from the ChatAssist API:

```
test "sentiment analysis returns valid structured output":
    response = send_chat_request(
        prompt: "Review: The product arrived quickly and works perfectly.",
        response_format: sentiment_schema
    )

    parsed = JSON.parse(response.body.choices[0].message.content)

    assert parsed.sentiment in ["positive", "negative", "neutral", "mixed"]
    assert parsed.confidence is a number between 0.0 and 1.0
    assert parsed.key_phrases is a non-empty array
    assert each item in parsed.key_phrases is a string
```

With `strict: true`, the model achieves 100% schema conformance. This means your format-level assertions will never fail due to model variation -- only due to actual bugs. **Structured Outputs are the first line of defense.** Whenever you can constrain the response format, do so.

---

## Section 3: Level 2 -- Content Containment (10 min)

Check for the presence or absence of specific content. These assertions are still deterministic -- a string either contains "Paris" or it does not -- but they accommodate the natural variation of GenAI output.

### What to Check

- **Required terms:** The response mentions a specific fact
- **Prohibited content:** The response does NOT contain sensitive information
- **Regex patterns:** The response contains data in the right format
- **Keyword coverage:** The response mentions at least N of M required topics

### Pseudo-code Examples

```
test "capital of France response contains the answer":
    response = send_chat_request(prompt: "What is the capital of France?")
    content = response.body.choices[0].message.content

    # Positive containment -- the key fact must appear
    assert "Paris" in content

    # This works whether the model says "The capital of France is Paris"
    # or "Paris is the capital city of France" or any other phrasing
```

```
test "customer support response does not leak PII":
    response = send_chat_request(
        prompt: "Generate a sample customer profile for testing."
    )
    content = response.body.choices[0].message.content

    # Negative containment -- prohibited content must NOT appear
    assert content does not match regex /\b\d{3}-\d{2}-\d{4}\b/    # no SSNs
    assert content does not match regex /\b[\w.]+@[\w.]+\.\w+\b/   # no emails
    assert content does not contain "555-"                          # no phone numbers
```

```
test "math tutor response covers required steps":
    response = send_chat_request(
        system: "You are a math tutor. Show your work.",
        prompt: "What is 20% of 240?"
    )
    content = response.body.choices[0].message.content

    # Keyword coverage -- key concepts must appear
    assert "48" in content                     # the correct answer
    assert "20" in content or "0.20" in content  # the percentage
    assert "240" in content                    # the original number
```

### Negative Assertions Are Critical

Verifying the *absence* of content is just as important as verifying its presence. In GenAI testing, negative assertions catch:

- PII leakage (real names, email addresses, phone numbers)
- Competitor mentions in branded responses
- Harmful instructions or inappropriate content
- System prompt leakage (internal rules appearing in user-facing output)

---

## Section 4: Level 3 -- Similarity-Based Assertions (10 min)

Compare meaning, not exact words. This level bridges the gap between simple containment checks and full semantic evaluation.

### Techniques

**Embedding cosine similarity:** Convert both the response and a reference text into numerical vectors (embeddings), then measure how close they are:

```
test "explanation is semantically similar to reference":
    response = send_chat_request(
        prompt: "Explain what an API is in simple terms."
    )
    content = response.body.choices[0].message.content

    reference = "An API is a way for software programs to communicate with each other,
                 like a waiter taking your order to the kitchen and bringing back food."

    similarity = cosine_similarity(embed(content), embed(reference))
    assert similarity >= 0.80
```

**ROUGE / BLEU scores:** Measure the overlap of word sequences (n-grams) between the response and a reference text. Useful when you have a known-good reference answer.

**Levenshtein distance:** Character-level edit distance. Useful for near-matches where the output should be very close to a reference but may have minor variations.

### Threshold Tuning

The threshold is the critical decision:

| Threshold | Effect |
|-----------|--------|
| Too strict (e.g., 0.95) | False failures -- valid responses get rejected because they use different words |
| Too loose (e.g., 0.50) | Missed regressions -- poor responses pass because the bar is too low |
| Sweet spot (0.75 - 0.85 for most cases) | Catches real problems without rejecting valid variation |

You must calibrate thresholds by running your assertions against a set of known-good and known-bad responses. There is no universal "right" threshold.

### The Visual Regression Analogy

If you have used visual regression testing, this is the same concept:

- A pixel-diff tool says "these screenshots are 97% similar -- pass."
- A similarity assertion says "this response is 0.85 similar to the reference -- pass."

Both use a tolerance threshold. Both need calibration. Both can produce false positives (real changes below the threshold) and false negatives (problems above the threshold). Your instincts from visual testing transfer directly.

---

## Section 5: Level 4 -- LLM-as-Judge (10 min)

The most powerful and most complex assertion type. You ask another model to evaluate the response.

### Core Patterns

**Binary classification (simplest, most reliable):**
```
test "response is polite and professional":
    response = send_chat_request(
        prompt: "I want a refund and I'm furious about the quality!"
    )
    content = response.body.choices[0].message.content

    judge_prompt = """
    You are evaluating a customer support response.

    Customer message: "I want a refund and I'm furious about the quality!"
    Support response: "{content}"

    Is this response polite and professional? Answer only YES or NO.
    """

    verdict = send_chat_request(prompt: judge_prompt, temperature: 0.0)
    assert verdict.content == "YES"
```

**Rubric-based scoring:**
```
test "response quality meets threshold":
    response = send_chat_request(prompt: customer_question)
    content = response.body.choices[0].message.content

    judge_prompt = """
    Rate the following customer support response on a scale of 1-5 for each criterion.

    Response: "{content}"

    Criteria:
    - Helpfulness (1-5): Does it address the customer's question?
    - Accuracy (1-5): Is the information correct?
    - Tone (1-5): Is it professional and empathetic?

    Respond as JSON: {"helpfulness": N, "accuracy": N, "tone": N}
    """

    scores = send_chat_request(prompt: judge_prompt, temperature: 0.0)
    parsed = JSON.parse(scores.content)
    assert parsed.helpfulness >= 4
    assert parsed.accuracy >= 4
    assert parsed.tone >= 3
```

**Faithfulness check:**
```
test "response only uses information from the provided context":
    context = "Our return policy allows returns within 30 days. Items must be unopened."

    response = send_chat_request(
        system: "Answer using only the provided policy. Policy: {context}",
        prompt: "Can I return a product after 2 months?"
    )
    content = response.body.choices[0].message.content

    judge_prompt = """
    Context: "{context}"
    Response: "{content}"

    Does this response contain ONLY information from the provided context?
    Does it make any claims not supported by the context?
    Answer YES if faithful, NO if it adds unsupported information.
    """

    verdict = send_chat_request(prompt: judge_prompt, temperature: 0.0)
    assert verdict.content == "YES"
```

### Best Practices for LLM-as-Judge

These guidelines come from research on reliable judge implementations:

1. **Define score meanings explicitly** -- "a score of 1 means the response is completely irrelevant; a score of 5 means it fully addresses the question with accurate details"
2. **Split complex criteria into separate evaluators** -- do not ask one judge to assess helpfulness, accuracy, and tone in a single prompt; run three separate evaluations and combine the scores
3. **Add chain-of-thought reasoning** -- ask the judge to explain its reasoning before giving a score; this makes failures auditable
4. **Use few-shot examples** -- include 2-3 labeled examples so the judge knows what a "4" looks like versus a "2"
5. **Set judge temperature to 0** -- maximize reproducibility of the judge's scores
6. **Calibrate against human labels** -- target Cohen's kappa greater than 0.8 agreement between the judge and human raters
7. **Run self-consistency checks** -- send the same input through the judge 3 times; if it gives different scores, the judge prompt needs work
8. **Watch for biases** -- judges tend to favor longer responses (verbosity bias) and responses presented first (position bias)

### The Critical Warning

LLM-as-judge adds its own layer of non-determinism. The judge can be wrong. It can be inconsistent. It can be biased. It is a tool, not an oracle.

**Never trust an LLM-as-judge in CI/CD without first validating it against human labels.** Build a labeled dataset of 50-200 examples, run the judge against it, measure agreement, and iterate on the judge prompt until you reach acceptable accuracy.

---

## Section 6: Level 5 -- Statistical Assertions (5 min)

For when single-run assertions are not enough. Instead of asking "did this test pass?" you ask "does this test pass *consistently*?"

### Patterns

**N-of-M pass criteria:**
```
test "response quality is consistent across runs":
    pass_count = 0
    for i in 1..5:
        response = send_chat_request(prompt: "Summarize our return policy.")
        content = response.body.choices[0].message.content
        if "30 days" in content and "original condition" in content:
            pass_count += 1

    assert pass_count >= 4 out of 5  # 80% pass rate required
```

**Average score across runs:**
```
test "average similarity stays above threshold":
    scores = []
    for i in 1..5:
        response = send_chat_request(prompt: test_prompt)
        similarity = cosine_similarity(embed(response.content), embed(reference))
        scores.append(similarity)

    assert average(scores) >= 0.80
    assert min(scores) >= 0.65    # no single run should be terrible
```

**Drift detection over time:**
Track assertion scores across test runs over days and weeks. A gradual decline in average scores signals model drift even when individual tests still pass.

Statistical assertions catch a specific failure mode: the response that is *usually* good but *sometimes* bad. A single test run might hit the good case and pass, hiding the problem. Running multiple times and asserting on consistency surfaces these issues.

---

## Red Flags: Assertion Anti-Patterns (5 min)

Before we close, here are patterns to avoid:

**Brittle snapshot matching:**
```
# BAD -- will fail whenever the model rephrases
assert response.content == "The capital of France is Paris."
```

**Exact string comparison on non-deterministic output:**
```
# BAD -- the model might say "Paris" or "paris" or "Paris, France"
assert response.content == expected_response
```

**No structural assertions at all:**
```
# BAD -- skips Level 1 entirely
# If the API returns an error, this test might still "pass"
# because it only checks the LLM-as-judge verdict
assert judge_says_good(response.content)
```

**Jumping straight to LLM-as-judge for everything:**
```
# BAD -- expensive, slow, and introduces its own non-determinism
# when a simple containment check would suffice
assert llm_judge("Does this response mention Paris?", response.content) == "YES"
# BETTER:
assert "Paris" in response.content
```

**The right approach is layered.** For a test that verifies a customer support response about return policy:

```
# Level 1: Structure
assert response.status_code == 200
assert response.body.choices[0].finish_reason == "stop"

# Level 2: Key facts present
assert "30 days" in content
assert "original condition" in content

# Level 2: Prohibited content absent
assert "full refund guaranteed" not in content  # don't overpromise

# Level 4: Overall quality (only if needed)
assert judge_verdict(content, "Is this response helpful and accurate?") == "YES"
```

Each layer catches different failure modes. Level 1 catches API errors. Level 2 catches factual omissions and unsafe content. Level 4 catches subtle quality issues that simpler checks miss.

---

## Discussion and Q&A (15 min)

Consider these questions:

- At which level would you start for your current project?
- What are the risks of jumping straight to LLM-as-judge?
- How do you decide the right similarity threshold? What data would you need?
- When would you invest in Level 5 (statistical) assertions? When would it be overkill?

---

## Session Deliverable: Assertion Strength Guide

### The Five-Level Ladder

| Level | Name | Cost | Speed | Determinism | Use When... |
|-------|------|------|-------|-------------|-------------|
| 1 | Structural | Free | Instant | Deterministic | Always -- every test should include this |
| 2 | Containment | Free | Instant | Deterministic | You know specific facts that must (or must not) appear |
| 3 | Similarity | Low | Fast | Semi-deterministic | Meaning matters more than exact wording |
| 4 | LLM-as-Judge | High | Slow | Non-deterministic | Quality, tone, or faithfulness must be assessed |
| 5 | Statistical | High | Slow | Varies | You need confidence across multiple runs |

### Decision Flowchart

```
Can you check the response shape/format?
  YES --> Add Level 1 assertions (always do this)

Are there specific facts, terms, or patterns that must appear?
  YES --> Add Level 2 containment assertions

Is there a reference answer you can compare against?
  YES --> Is exact wording important?
    YES --> Use Level 2 (containment)
    NO  --> Use Level 3 (similarity)

Do you need to assess subjective quality (helpfulness, tone, faithfulness)?
  YES --> Add Level 4 (LLM-as-judge). Validate the judge first!

Is the response sometimes good and sometimes bad for the same input?
  YES --> Add Level 5 (statistical). Run N times, assert on consistency.
```

### When NOT to Use Each Level

| Level | Anti-pattern |
|-------|-------------|
| 1 | Never skip this level. It is always appropriate. |
| 2 | Do not use for creative/open-ended outputs where specific terms are not expected |
| 3 | Do not use when you do not have a reliable reference text to compare against |
| 4 | Do not use for checks that Level 2 can handle (e.g., "Does it mention Paris?") |
| 5 | Do not use when single-run assertions already give sufficient confidence |

### Layering Guide

For most GenAI API tests, combine levels:

- **Minimum:** Level 1 (structural)
- **Standard:** Level 1 + Level 2 (structural + containment)
- **Thorough:** Level 1 + Level 2 + Level 3 or Level 4
- **Critical path:** Level 1 + Level 2 + Level 4 + Level 5
