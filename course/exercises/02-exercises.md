# Session 2 Exercises: Assertion Level Selector

**Duration:** 20 minutes
**Format:** Paper-based (no tools required)

---

## Setup

Below are ten test scenarios using the ChatAssist API. Each describes what the test should verify. For each scenario, you will recommend assertion levels, write the assertions in plain English, and justify your choices.

---

## Scenarios

### Scenario 1: Capital City Fact Check

The ChatAssist API is asked: "What is the capital of Germany?" The response should correctly identify Berlin as the capital.

**Sample response:** `"Berlin is the capital and largest city of Germany, located in northeastern Germany."`

### Scenario 2: Sentiment Classification

The ChatAssist API uses structured output to classify a product review: "Terrible quality, broke after one day. Total waste of money." The response must be valid JSON with a `sentiment` field set to `"negative"`.

**Sample response:** `"{\"sentiment\":\"negative\",\"confidence\":0.97,\"key_phrases\":[\"terrible quality\",\"broke after one day\",\"waste of money\"]}"`

### Scenario 3: Return Policy Response

A customer asks a support chatbot: "What is your return policy?" The system prompt says the return window is 30 days and items must be in original condition. The response should accurately state the policy without making promises not in the policy (like "full refund guaranteed").

**Sample response:** `"We offer a 30-day return window from the date of purchase. Items must be in their original condition with all tags attached. To initiate a return, please visit your order history."`

### Scenario 4: Order Status with Tool Call

A customer asks "Where is my order #55555?" The model should call the `lookup_order` tool with `order_id: "55555"`. After receiving tool results showing the order is "in transit" with carrier "QuickShip", the final response should include the tracking information.

**Sample tool call:** `{"name": "lookup_order", "arguments": "{\"order_id\": \"55555\"}"}`
**Sample final response:** `"Your order #55555 is currently in transit with QuickShip. Your tracking number is QS-77432 and the estimated delivery is March 5."`

### Scenario 5: Creative Product Description

The marketing team uses ChatAssist to generate product descriptions for a wireless headphone. Each description should be unique and engaging. The product features are: noise cancellation, 40-hour battery, Bluetooth 5.3.

**Sample response:** `"Immerse yourself in pure sound with our wireless headphones featuring advanced noise cancellation. With a marathon 40-hour battery life and Bluetooth 5.3, your music never misses a beat."`

### Scenario 6: Math Tutor Step-by-Step

A math tutor chatbot is asked: "What is 35% of 600?" It should show its work step by step and arrive at the correct answer of 210.

**Sample response:** `"Let's solve this step by step:\n\nStep 1: Convert 35% to a decimal: 35/100 = 0.35\nStep 2: Multiply: 0.35 x 600 = 210\n\nSo 35% of 600 is 210."`

### Scenario 7: Safety Filter Verification

A test sends a clearly inappropriate prompt to the ChatAssist API with `safety.level: "strict"`. The model should refuse to answer, returning `finish_reason: "safety"`.

**Sample response:** `finish_reason: "safety"`, content: `"I'm unable to provide information on that topic."`

### Scenario 8: PII Check in Generated Content

The ChatAssist API is asked to "Generate a sample customer profile for demonstration purposes." The response should NOT contain any real-looking personally identifiable information such as real email addresses, phone numbers, or social security numbers.

**Sample response:** `"Here's a sample profile: Name: Jane Smith, Email: jane.smith@example.com, Phone: (555) 012-3456, Membership: Gold tier since 2022."`

### Scenario 9: Multi-Language Consistency

The ChatAssist API is asked the same factual question in English and Spanish: "What year was the Eiffel Tower completed?" Both responses should contain the year 1889, regardless of the language of the rest of the response.

**English response:** `"The Eiffel Tower was completed in 1889."`
**Spanish response:** `"La Torre Eiffel fue completada en 1889."`

### Scenario 10: Long-Form Summary Quality

The ChatAssist API summarizes a 5-page product safety report. The summary should be accurate, concise (under 200 words), cover all major findings, and not add any information not in the original report.

**Sample response:** `"The Q3 safety review identified three findings: (1) the battery housing seal fails above 95C, exceeding thermal spec by 15C; (2) the charging cable insulation meets UL standards but shows wear after 500 insertion cycles; (3) no issues were found with the power management firmware. Recommended actions include redesigning the battery seal for higher temperature tolerance and sourcing higher-durability cable insulation."`

---

## Tasks

### Task 1: Recommend Assertion Levels

For each scenario, recommend which assertion level(s) to use:

| Scenario | Level(s) | Brief Justification |
|----------|----------|---------------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
| 9 | | |
| 10 | | |

### Task 2: Write the Assertions

For each scenario, write the assertions in plain English. Be specific. Example format:

> "Assert that the response status is 200, the content contains 'Berlin', and the content does not contain any phone numbers."

### Task 3: Justify the Level

For **two** scenarios, explain:
1. Why a *lower* assertion level would be insufficient
2. Why a *higher* assertion level would be overkill

### Task 4: Write a Judge Prompt

For the scenarios where you recommended LLM-as-judge (Level 4), write the actual judge prompt you would use. Include:
- What the judge should evaluate
- What criteria to apply
- What format the judge should respond in

### Task 5: Identify a Layered Assertion

Pick **one** scenario where you would use multiple levels together. Write out all the assertion layers and explain what each layer catches that the others would miss.

---

## Solution Notes

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
