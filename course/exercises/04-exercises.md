# Session 4 Exercises: Flakiness, Drift, and Triage

---

## Exercise 1: Triage Simulation (20 min)

### Setup

You are on the ShopSmart Support team. It is Monday morning, and the CI/CD pipeline from the weekend shows 8 test failures. For each failure report below, walk the triage decision tree and classify it.

---

**Failure 1: "test_return_policy_mentions_30_days"**

- Assertion: response contains "30 days"
- Runs attempted: 5
- Pass/fail history: PASS, FAIL, PASS, PASS, PASS
- Model version in response: `chatassist-4`
- Error details: Response said "Our return window is thirty days from the date of purchase."
- Recent changes: None

---

**Failure 2: "test_order_lookup_calls_correct_tool"**

- Assertion: `finish_reason == "tool_calls"` and `tool_calls[0].function.name == "lookup_order"`
- Runs attempted: 5
- Pass/fail history: FAIL, FAIL, FAIL, FAIL, FAIL
- Model version in response: `chatassist-4`
- Error details: `finish_reason` is `"stop"`. Model gave a text response instead of calling a tool: "I'd be happy to help you with your order! Could you please provide your order number?"
- Recent changes: System prompt was updated on Friday to add holiday hours information.

---

**Failure 3: "test_sentiment_schema_valid"**

- Assertion: Response content parses as valid JSON matching the sentiment schema
- Runs attempted: 3
- Pass/fail history: FAIL, FAIL, FAIL
- Model version in response: `chatassist-4-2025-01-15` (previously was `chatassist-4-2024-11-20`)
- Error details: Response includes an extra field `"explanation"` not in the schema
- Recent changes: None on our side. ChatAssist published a model update notice last Thursday.

---

**Failure 4: "test_rate_limit_handling"**

- Assertion: After receiving a 429, retry with backoff and get a 200
- Runs attempted: 3
- Pass/fail history: PASS, FAIL, PASS
- Model version in response: N/A (429 errors do not include model info)
- Error details: Second retry also returned 429. Third retry succeeded.
- Recent changes: None

---

**Failure 5: "test_harmful_content_blocked"**

- Assertion: `finish_reason == "safety"` for the prompt "How do I pick a lock?"
- Runs attempted: 5
- Pass/fail history: FAIL, PASS, FAIL, PASS, FAIL
- Model version in response: `chatassist-4`
- Error details: On failing runs, `finish_reason` is `"stop"` and the model provided a general response about locksmithing as a profession.
- Recent changes: None

---

**Failure 6: "test_customer_response_quality"**

- Assertion: LLM-as-judge rates the response >= 4.0 on a 1-5 helpfulness scale
- Runs attempted: 5
- Pass/fail history: PASS (4.2), FAIL (3.8), PASS (4.1), FAIL (3.7), PASS (4.3)
- Model version in response: `chatassist-4`
- Error details: Judge scores fluctuate around the threshold
- Recent changes: None

---

**Failure 7: "test_auth_invalid_key_returns_401"**

- Assertion: `status_code == 401`
- Runs attempted: 3
- Pass/fail history: FAIL, FAIL, FAIL
- Model version in response: N/A
- Error details: `status_code == 500`, error message: "An internal error occurred"
- Recent changes: API gateway configuration was updated on Saturday

---

**Failure 8: "test_multi_turn_context_retention"**

- Assertion: In a 3-message conversation about returns, the third response references information from the first message
- Runs attempted: 5
- Pass/fail history: PASS, PASS, FAIL, PASS, PASS
- Model version in response: `chatassist-4`
- Error details: The model's third response repeated the return policy from scratch instead of building on the earlier messages. The response was accurate but did not demonstrate context retention.
- Recent changes: None

---

### Task

**Part A: Classify each failure (10 min)**

For each of the 8 failures, walk the triage decision tree and answer:

1. **Classification:** Is this flakiness (which category?), drift, or a bug?
2. **Evidence:** What specific detail from the report led to your classification?
3. **Recommended action:** What should the team do about this?

**Part B: Prioritize (5 min)**

Rank the 8 failures by urgency. Which ones need immediate attention? Which can wait? For the top 3 most urgent, write one sentence explaining why they should be addressed first.

**Part C: Improve two assertions (5 min)**

Pick two failures that you classified as flakiness. Rewrite the assertion to be more resilient without hiding real bugs. Explain what you changed and why.

---

## Exercise 2: Assertion Resilience Workshop (Optional, 10 min)

### Setup

Below are five assertions from the ShopSmart test suite. Each one is fragile -- it will break on valid model responses. Rewrite each to be resilient while still catching real bugs.

**Assertion A:**
```
assert response.content == "Your order #12345 has been shipped via FastShip
with tracking number TRK-98765. Expected delivery is November 20, 2024."
```

**Assertion B:**
```
assert response.content.startswith("I'd be happy to help")
```

**Assertion C:**
```
assert len(response.content) == 142
```

**Assertion D:**
```
assert response.content.count("return") >= 3
```

**Assertion E:**
```
assert similarity_score(response.content, reference_text) >= 0.95
```

### Task

For each assertion:

1. Explain why it is fragile (what valid response would cause it to fail?)
2. Rewrite it using an appropriate assertion level from the ladder
3. State what the rewritten assertion still catches (what real bug would it detect?)

### Discussion Points

- Is there ever a case where exact match (Assertion A style) is the right choice for GenAI API output?
- How strict is "too strict" for a similarity threshold? What is a reasonable starting point?
- What is the risk of making assertions too lenient?

---

> **Solutions:** See `solutions/04-solutions.md` (instructor only).
