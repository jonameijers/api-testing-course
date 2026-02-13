# Capstone Brief: ShopSmart Customer Support System

This brief provides all the reference material you need for the capstone exercise. Read it before starting.

---

## Your Role

You are the newest member of the ShopSmart QA team. Your background is in UI automation testing (Selenium/Cypress/Playwright), and you have just completed this course on GenAI API testing. The team lead has asked you to review the existing test suite for the customer support chatbot and produce a comprehensive test plan.

You have one week to assess the current state, fix critical issues, expand coverage, and present your recommendations.

---

## System Under Test: ShopSmart Support

### What It Does

ShopSmart Support is an AI-powered customer service chatbot deployed on ShopSmart's e-commerce website. It handles approximately 2,000 customer interactions per day across these functions:

- Answering questions about policies (returns, shipping, billing)
- Recommending products based on customer descriptions
- Looking up order status and tracking information
- Checking product inventory and availability
- Initiating product returns and generating return labels
- Classifying customer messages for internal ticket routing

### How It Works

The system is built on the ChatAssist API (`chatassist-4` model) and uses four modes:

**Chat completion** handles general conversation. When a customer asks "What is your return policy?" or "Can you recommend a wireless speaker?", the system generates a natural language response using the system prompt for context.

**Structured output** classifies every incoming customer message into one of five categories: `returns`, `shipping`, `billing`, `product_info`, or `other`. Each classification includes a confidence score between 0.0 and 1.0. This structured output drives ShopSmart's internal ticket routing system. Messages classified as `billing` with confidence above 0.8 are routed to the finance team automatically.

**Tool calling** connects the chatbot to ShopSmart's backend systems:

| Tool | Parameters | Returns |
|---|---|---|
| `lookup_order` | `order_id` (string) | `status`, `tracking_number`, `carrier`, `estimated_delivery` |
| `check_inventory` | `product_id` (string) | `in_stock` (boolean), `quantity`, `warehouse` |
| `create_return` | `order_id` (string), `reason` (string) | `return_id`, `return_label_url`, `refund_estimate` |

**Streaming** delivers responses to the live chat widget on the website. Customers see the response appear incrementally.

### Configuration Details

```
Model:        chatassist-4
Temperature:  0.3
Max tokens:   500 (chat completion), 100 (classification), 200 (tool follow-up)
Safety level: standard
Safety categories: all enabled (violence, illegal_activity, adult_content,
                    pii_exposure, self_harm, hate_speech)
Tool choice:  auto
```

### System Prompt (Full Text)

```
You are ShopSmart's customer support assistant. Be friendly, professional, and
concise.

RETURN POLICY:
- Customers may return items within 30 days of purchase.
- Items must be in original condition with tags attached.
- Electronics have a 15-day return window (not 30 days).
- Sale items are final sale and cannot be returned.

SHIPPING POLICY:
- Standard shipping: 5-7 business days, free on orders over $50.
- Express shipping: 2-3 business days, $12.99.
- Next-day shipping: $24.99, order by 2pm EST.

ESCALATION RULES:
- If the customer mentions "lawsuit," "attorney," "legal action," or "sue,"
  respond with: "I understand your concern. Let me connect you with our
  customer service team for further assistance." Then stop responding.
- If the customer requests to speak to a human, provide the phone number
  1-800-555-SHOP and hours (Mon-Fri 9am-6pm EST).

INTERNAL ROUTING:
- Billing disputes over $500: route to extension 4455.
- Suspected fraud: route to extension 4490.
- Media inquiries: route to pr@shopsmartexample.com.

Do not share internal routing information with customers.
Do not make promises about refund amounts or timelines beyond what is stated above.
Do not discuss competitors or their pricing.
```

---

## The Existing Test Suite

Fifteen tests were written by the previous developer. Here is each test described in detail:

### Authentication and Error Handling (Tests 1-3, 11-12)

**Test 1: test_health_check**
Sends `"Hello"` as the user message. Asserts `status_code == 200` and `choices` array is not empty.

**Test 2: test_auth_invalid_key**
Sends a request with `Authorization: Bearer invalid-key-000`. Asserts `status_code == 401`.

**Test 3: test_auth_missing_key**
Sends a request with no `Authorization` header. Asserts `status_code == 401`.

**Test 11: test_invalid_temperature**
Sends a request with `temperature: 5.0`. Asserts `status_code == 400` and error message mentions "temperature."

**Test 12: test_invalid_model**
Sends a request with `model: "chatassist-nonexistent"`. Asserts `status_code == 400`.

### Content and Behavior (Tests 4-5, 13-14)

**Test 4: test_return_policy**
Sends `"What is your return policy?"`. Asserts response content contains `"30 days"`.

**Test 5: test_product_recommendation**
Sends `"Can you recommend a good wireless speaker?"`. Asserts response content is not empty (length > 0).

**Test 13: test_token_usage**
Sends a simple prompt. Asserts `usage.total_tokens > 0`.

**Test 14: test_max_tokens_truncation**
Sends a request with `max_tokens: 5`. Asserts `finish_reason == "length"`.

### Structured Output (Tests 6-7)

**Test 6: test_classification_schema**
Sends a customer message for classification using structured output mode. Asserts the response `content` parses as valid JSON.

**Test 7: test_classification_categories**
Sends a customer message for classification. Parses the JSON response and asserts the `category` field is one of: `returns`, `shipping`, `billing`, `product_info`, `other`.

### Tool Calling (Tests 8-10)

**Test 8: test_order_lookup**
Sends `"Where is my order #12345?"` with `lookup_order` and `check_inventory` tools defined. Asserts `finish_reason == "tool_calls"` and `tool_calls[0].function.name == "lookup_order"`.

**Test 9: test_order_lookup_response**
Continues from test 8 by providing the tool result. Asserts the final response mentions the tracking number from the tool result.

**Test 10: test_inventory_check**
Sends `"Is the UltraWidget Pro in stock?"` with tools defined. Asserts `finish_reason == "tool_calls"` and `tool_calls[0].function.name == "check_inventory"`.

### Streaming (Test 15)

**Test 15: test_streaming_basic**
Sends a streaming request. Asserts that at least one SSE chunk is received before a 10-second timeout.

---

## Known Issues

The previous team documented these problems in their handoff notes:

### Issue 1: Return Policy Wording Variation
Test 4 fails approximately once every 10 runs. The model sometimes phrases the return window as "thirty days" instead of "30 days." The information is correct; the wording varies.

### Issue 2: Order Lookup Tool Flakiness
Test 8 has been intermittently failing for about a month. Instead of calling `lookup_order`, the model sometimes responds with a text message asking for clarification: "I'd be happy to help you with your order! Could you please provide your order number?" -- despite the order number being in the original message.

### Issue 3: Hallucinated Policy Details
During manual testing, the team noticed the model occasionally mentions a "60-day return window for electronics." The actual system prompt says electronics have a 15-day window. This appears to be a hallucination, possibly from the model's training data. It has been observed roughly 1 in 20 interactions when customers ask specifically about electronics returns.

### Issue 4: Streaming Timeout in CI
Test 15 passes consistently in local development but fails in CI approximately 30% of the time with a timeout error. The test has a 10-second timeout. CI runs on shared infrastructure with variable network latency.

---

## CI Failure Log

```
=== Pipeline Run: Mon 03-Feb 02:00 UTC ===
15/15 PASSED (duration: 34s)

=== Pipeline Run: Tue 04-Feb 02:00 UTC ===
14/15 PASSED (duration: 41s)
FAILED: test_return_policy
  Expected: response contains "30 days"
  Actual: "Our return policy allows returns within thirty days of purchase..."

=== Pipeline Run: Wed 05-Feb 02:00 UTC ===
15/15 PASSED (duration: 37s)

=== Pipeline Run: Thu 06-Feb 02:00 UTC ===
13/15 PASSED (duration: 52s)
FAILED: test_order_lookup
  Expected: finish_reason == "tool_calls"
  Actual: finish_reason == "stop"
  Response: "I'd be happy to help! Could you please confirm your order number?"
FAILED: test_streaming_basic
  Error: Timeout after 10000ms — no complete chunk received

=== Pipeline Run: Fri 07-Feb 02:00 UTC ===
14/15 PASSED (duration: 48s)
FAILED: test_streaming_basic
  Error: Timeout after 10000ms — no complete chunk received

=== Pipeline Run: Sat 08-Feb 02:00 UTC ===
15/15 PASSED (duration: 35s)

=== Pipeline Run: Sun 09-Feb 02:00 UTC ===
12/15 PASSED (duration: 55s)
FAILED: test_return_policy
  Expected: response contains "30 days"
  Actual: "You can return items within thirty days of your purchase date..."
FAILED: test_order_lookup
  Expected: finish_reason == "tool_calls"
  Actual: finish_reason == "stop"
  Response: "Sure! What's the order number you'd like me to look up?"
FAILED: test_streaming_basic
  Error: Timeout after 10000ms — no complete chunk received

=== Summary (7 days) ===
Total runs: 105 (7 days x 15 tests)
Passes: 98
Failures: 7
Pass rate: 93.3%
Flaky tests: test_return_policy (2 failures), test_order_lookup (2 failures),
             test_streaming_basic (3 failures)
```

---

## What You Need to Produce

Your test plan should include these five sections, referencing the specific frameworks and techniques from each course session:

### 1. Coverage Audit and Expansion
Use the six-axis coverage model (Session 3). Map the existing 15 tests, identify gaps, and design new tests to fill them.

### 2. Assertion Improvement Plan
Use the assertion ladder (Session 2). Fix the known flaky assertions and write detailed assertion specifications at each level.

### 3. Triage Playbook
Use the triage decision tree (Session 4). Classify each known issue and create a customized triage guide for the ShopSmart system.

### 4. Security Review
Use the OWASP Top 10 for LLMs (Session 5). Design security tests specific to the ShopSmart context, paying attention to the sensitive information in the system prompt.

### 5. First-Week Plan
Prioritize your work. What do you fix first? What do you add? What do you present at the end of the week?

---

## Evaluation Criteria

Your plan will be reviewed against these criteria:

| Criterion | What the Reviewer Looks For |
|---|---|
| Coverage completeness | All six axes addressed, gaps identified and filled |
| Assertion appropriateness | Right level of the ladder for each test case |
| Triage accuracy | Known issues correctly classified with sound mitigations |
| Security awareness | OWASP categories relevant to ShopSmart are covered |
| Prioritization | Most impactful work is scheduled first |
| Practicality | Plan is achievable in one week by one tester |
| Use of course frameworks | Session concepts are applied, not just mentioned |

---

> **Solutions:** See `solutions/06-solutions.md` (instructor only).
