# Session 2 Solutions: Assertion Level Selector

> These are the solution notes for the Session 2 exercises. Do not distribute to participants before the session.

---

### Task 1: Recommended Levels

| Scenario | Level(s) | Brief Justification |
|----------|----------|---------------------|
| 1 | 1 + 2 | Structural check + contains "Berlin" |
| 2 | 1 | Structured output -- schema validation is sufficient |
| 3 | 1 + 2 + 4 | Structure + key facts + quality/faithfulness check |
| 4 | 1 + 2 | Structure + tool call correctness + key facts in final answer |
| 5 | 1 + 2 + 3 | Structure + feature keywords + similarity to reference |
| 6 | 1 + 2 | Structure + contains "210" and step-by-step markers |
| 7 | 1 | Structural -- check finish_reason is "safety" |
| 8 | 1 + 2 | Structure + negative assertions (no real PII patterns) |
| 9 | 1 + 2 + 5 | Structure + contains "1889" + statistical consistency across languages |
| 10 | 1 + 2 + 4 | Structure + word count + faithfulness judge |

### Task 2: Assertions in Plain English

**Scenario 1:** Assert status is 200, response has valid structure, content contains "Berlin", finish_reason is "stop".

**Scenario 2:** Assert status is 200, content is valid JSON, parsed JSON has "sentiment" field equal to "negative", "confidence" is a number between 0 and 1, "key_phrases" is a non-empty array of strings.

**Scenario 3:** Assert status is 200, content contains "30 days", content contains "original condition", content does NOT contain "full refund guaranteed" or "money back guarantee", LLM-as-judge confirms response is faithful to the provided policy.

**Scenario 4:** Assert the first response has finish_reason "tool_calls", tool_calls array contains a call to "lookup_order" with order_id "55555". After providing tool results, assert the final response contains "in transit" or "QuickShip", and the tracking number.

**Scenario 5:** Assert status is 200, content mentions "noise cancellation" (or close variant), "40-hour" or "40 hour", and "Bluetooth 5.3". Cosine similarity to a reference description is above 0.70 (but not too strict -- variety is desired).

**Scenario 6:** Assert status is 200, content contains "210" (the answer), content contains "0.35" or "35%" (the conversion step), content contains "600" (the original number).

**Scenario 7:** Assert finish_reason is "safety". Assert safety_metadata.blocked is true.

**Scenario 8:** Assert status is 200. Assert content does NOT match SSN pattern (XXX-XX-XXXX). Assert content does NOT match phone patterns with real area codes. Assert email addresses use example.com or similar placeholder domains.

**Scenario 9:** Assert both responses return 200. Assert both contain "1889". Run each prompt 3 times and assert "1889" appears in all runs (statistical).

**Scenario 10:** Assert status is 200. Assert word count is under 200. Assert content contains key finding terms. LLM-as-judge checks faithfulness: "Does this summary only contain information from the original report?"

### Task 3: Example Justification -- Scenario 3

**Why Level 2 alone is insufficient:** Containment checks can verify that "30 days" and "original condition" appear, but they cannot detect if the response *adds* a promise like "We'll process your refund within 24 hours" that is not in the policy. You need Level 4 (faithfulness judge) to catch fabricated commitments.

**Why Level 5 (statistical) would be overkill:** With temperature set low for a support chatbot, the responses will be consistent enough that a single-run assertion gives confidence. Running 5 times would add cost without catching meaningful variation.

### Task 4: Judge Prompt Example -- Scenario 3

```
You are evaluating a customer support chatbot's response about a return policy.

The actual return policy is:
- Returns accepted within 30 days of purchase
- Items must be in original condition with tags attached
- Returns can be initiated from the order history page

The chatbot's response was:
"{content}"

Evaluate the response on two criteria:

1. ACCURACY: Does the response correctly state the policy details above?
   Answer YES if all stated facts match the policy. Answer NO if any facts are wrong.

2. FAITHFULNESS: Does the response ONLY contain information from the policy?
   Answer YES if everything in the response is supported by the policy.
   Answer NO if the response adds promises, guarantees, or details not in the policy.

Respond in this exact format:
ACCURACY: YES or NO
FAITHFULNESS: YES or NO
REASONING: one sentence explaining your judgment
```

### Task 5: Layered Assertion Example -- Scenario 10

```
# Level 1: Structure
assert response.status_code == 200
assert response.body.choices[0].finish_reason == "stop"
assert response.body.usage.total_tokens > 0
--> Catches: API errors, malformed responses, truncated output

# Level 2: Containment
assert word_count(content) <= 200
assert "battery" in content.lower()        # major finding 1
assert "charging cable" in content.lower()  # major finding 2
assert content does not contain information about unrelated products
--> Catches: summaries that are too long, miss major findings, or go off-topic

# Level 4: Faithfulness judge
judge_verdict = ask_judge("Does this summary only contain
    information from the original report? Does it cover the
    three main findings?")
assert judge_verdict.faithful == "YES"
assert judge_verdict.complete == "YES"
--> Catches: hallucinated findings, omitted critical details,
    subtle additions not in the source material
```

Each layer catches failures the other layers miss:
- Level 1 catches transport-layer failures (the response was not even valid)
- Level 2 catches obvious content problems (key findings missing, response too long)
- Level 4 catches subtle quality issues (hallucinated details, unfaithful summaries)
