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

> **Solutions:** See `solutions/02-solutions.md` (instructor only).
