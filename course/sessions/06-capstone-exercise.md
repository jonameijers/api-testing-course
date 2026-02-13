# Capstone: Put It All Together

**Duration:** 90 minutes
**Deliverable:** Complete Test Plan for the ShopSmart ChatAssist System

---

## Learning Objectives

By the end of this session, you will be able to:

1. Design a complete test plan for a GenAI API application from scratch
2. Apply all course concepts: HTTP fundamentals, GenAI differences, assertion ladder, coverage model, triage approach, and security
3. Justify your testing decisions by referencing course frameworks
4. Present and defend a test plan to peers

---

## Bridge from UI Testing (10 min)

**What you know from UI testing:**
You have written test plans before. You know how to break an application into testable pieces, prioritize by risk, organize by area, and document your approach. You have done this for web applications, and the skills transfer directly.

**What is different here:**

| What You Would Do for a Web App | What You Do for a GenAI API Application |
|---|---|
| Map pages and user flows | Map API modes and interaction patterns |
| Write pixel-perfect assertions | Use the assertion ladder (L1 through L5) |
| Build a browser/device matrix | Build a parameter/mode coverage matrix |
| Debug flaky tests caused by timing | Triage failures caused by non-determinism and drift |
| Test for XSS and SQL injection | Test for prompt injection and PII leakage |
| Test login and authorization | Test API key authentication and agent permissions |

**Key insight:** This is not a new discipline. It is your discipline -- applied to a new kind of system. The capstone proves that.

---

## The Scenario: ShopSmart Customer Support

### Company Background

ShopSmart is a mid-size e-commerce company selling home goods and electronics. They have deployed an AI-powered customer support system built on the ChatAssist API. The system handles approximately 2,000 customer interactions per day.

### System Architecture

The ShopSmart support system uses all four ChatAssist API modes:

**Chat completion** for general customer inquiries -- return policy questions, product recommendations, complaint handling, and general FAQ responses. This is the primary mode, handling about 60% of interactions.

**Structured output** for ticket classification -- every customer message is classified into one of five categories (`returns`, `shipping`, `billing`, `product_info`, `other`) with a confidence score. This classification drives routing in ShopSmart's internal ticketing system.

**Tool calling** with three tools:
- `lookup_order(order_id)` -- returns order status, tracking number, carrier, and estimated delivery date
- `check_inventory(product_id)` -- returns current stock count and warehouse location
- `create_return(order_id, reason)` -- initiates a return process and generates a return shipping label

**Streaming** for the live chat interface on ShopSmart's website. Customers see the response appear incrementally, similar to watching someone type.

### Configuration

- Model: `chatassist-4`
- Temperature: `0.3` (tuned for consistency while allowing natural variation)
- Safety level: `standard`, all safety categories enabled
- System prompt: Contains ShopSmart's return policy (30 days, original condition), tone guidelines (friendly, professional, concise), escalation rules (mention of "lawsuit" or "attorney" triggers handoff), and internal routing notes

### The Existing Test Suite

The team that built the system left behind 15 tests. Here is what they cover:

| # | Test Name | What It Does |
|---|---|---|
| 1 | test_health_check | Sends a simple prompt, asserts status 200 |
| 2 | test_auth_invalid_key | Sends invalid API key, asserts 401 |
| 3 | test_auth_missing_key | Sends no API key, asserts 401 |
| 4 | test_return_policy | Asks about return policy, asserts response contains "30 days" |
| 5 | test_product_recommendation | Asks for a product recommendation, asserts response is not empty |
| 6 | test_classification_schema | Sends a message for classification, asserts response parses as valid JSON |
| 7 | test_classification_categories | Sends a message for classification, asserts category is one of the 5 valid values |
| 8 | test_order_lookup | Asks "Where is my order #12345?", asserts model calls `lookup_order` |
| 9 | test_order_lookup_response | Provides tool result, asserts final response mentions tracking number |
| 10 | test_inventory_check | Asks about product availability, asserts model calls `check_inventory` |
| 11 | test_invalid_temperature | Sends temperature: 5.0, asserts 400 error |
| 12 | test_invalid_model | Sends model: "nonexistent", asserts 400 error |
| 13 | test_token_usage | Asserts `usage.total_tokens > 0` on a successful response |
| 14 | test_max_tokens_truncation | Sends request with max_tokens: 5, asserts `finish_reason == "length"` |
| 15 | test_streaming_basic | Opens a streaming request, asserts at least one chunk is received |

### Known Issues (from the team's handoff notes)

1. "Test 4 (return policy) fails about once every 10 runs. The model sometimes says 'thirty days' instead of '30 days.'"
2. "Test 8 (order lookup) has been flaky since last month. Sometimes the model asks for the order number instead of calling the tool, even though the order number is in the message."
3. "We noticed the model sometimes mentions a '60-day return window for electronics' -- this is not in our return policy. Not sure where it comes from."
4. "The streaming test (15) passes in local dev but fails in CI about 30% of the time with a timeout error."

### CI Failure Log (Last 7 Days)

```
Mon 03-Feb: 15/15 passed
Tue 04-Feb: 14/15 passed (test_return_policy FAILED - "thirty days" vs "30 days")
Wed 05-Feb: 15/15 passed
Thu 06-Feb: 13/15 passed (test_order_lookup FAILED, test_streaming_basic FAILED - timeout)
Fri 07-Feb: 14/15 passed (test_streaming_basic FAILED - timeout)
Sat 08-Feb: 15/15 passed
Sun 09-Feb: 12/15 passed (test_return_policy FAILED, test_order_lookup FAILED,
                           test_streaming_basic FAILED - timeout)
```

---

## Capstone Exercise (60 min)

Your task: design a complete test plan for the ShopSmart ChatAssist system. You are the new GenAI API tester on the team. Your plan must address the existing test suite's gaps, the known issues, and your own analysis.

### Part 1: Coverage Audit and Expansion (15 min)

**A. Audit the existing 15 tests.**
Map each test to the six-axis coverage model from Session 3. Identify which axes are well-covered and which have gaps.

**B. Design at least 10 additional test cases** to fill the most critical gaps. For each new test, specify:
- Test ID and name
- Which coverage axis it addresses
- Which ChatAssist mode it tests
- Priority (P0-P3)
- Assertion level (L1-L5)
- CI/CD tier (Fast / Standard / Deep)
- One-sentence description of what the test verifies

**C. Assign every test (existing + new) to a CI/CD tier.** Count the totals per tier and verify the distribution makes sense: Fast tier should be the largest, Deep tier the smallest.

### Part 2: Assertion Improvement Plan (15 min)

**A. Fix the flaky tests.** For each of the 4 known issues, classify it using the triage decision tree from Session 4, then propose a specific fix:

1. test_return_policy ("thirty days" vs "30 days")
2. test_order_lookup (sometimes asks for order number instead of calling tool)
3. The "60-day return window for electronics" hallucination
4. test_streaming_basic (CI timeout failures)

**B. Write detailed assertions for 5 critical test cases** -- one from each assertion level:
- Level 1 (Structural): Write the structural checks
- Level 2 (Containment): Write the containment patterns (what to check for, what to check against)
- Level 3 (Similarity): Describe the reference text and threshold
- Level 4 (LLM-as-judge): Write the full judge prompt, including evaluation criteria and scoring rubric
- Level 5 (Statistical): Specify the number of runs, pass threshold, and what metric you are tracking

### Part 3: Triage Playbook (10 min)

**A. Customize the triage decision tree** for ShopSmart's specific context. Add branches or notes that are specific to this application -- for example, how to handle the known tool calling flakiness.

**B. Identify the top 3 most likely flakiness scenarios** for the ShopSmart system (beyond the known issues). For each, specify:
- What would the failure look like?
- Which flakiness category does it fall into?
- What mitigation would you put in place?

**C. Describe your drift detection strategy.** How would you detect that the ChatAssist model has been updated? What tests would you run first when a model update is detected?

### Part 4: Security Review (10 min)

**A. Design 5 prompt injection test cases** targeting the ShopSmart context specifically. Think about what an attacker would try to extract (return policy escalation rules, internal routing extension, or manipulation of tool calls).

**B. Design 3 PII leakage scenarios** relevant to an e-commerce support system (customers share order numbers, email addresses, payment information).

**C. Design 2 tool calling abuse scenarios.** How could an attacker misuse `lookup_order`, `check_inventory`, or `create_return`? For example: looking up other customers' orders, or initiating unauthorized returns.

**D. Write a test environment security checklist** for the ShopSmart QA team. What practices should they follow when setting up and maintaining their GenAI API test suite?

### Part 5: First-Week Plan (10 min)

You start on Monday. Plan your first 5 days.

**A. Day 1-2: What do you fix first?** Which of the known issues and coverage gaps are most urgent? Justify your ordering.

**B. Day 3-4: What do you add?** Which new tests from your coverage expansion go in first? Which tier do they join?

**C. Day 5: What do you present to the team?** Summarize the state of the test suite: what was there, what you changed, what gaps remain, and what your recommended next steps are.

**D. Identify the single most important test case in your plan** (existing or new). In 2-3 sentences, explain why it matters more than any other.

---

## Group Presentations and Review (20 min)

Each group presents their test plan (5 minutes per group):

1. State your top finding from the coverage audit (biggest gap)
2. Walk through your fix for one of the known issues
3. Present your most creative security test case
4. Share your "single most important test" and justify it

**Peer review criteria:**
- Does the plan use the six-axis coverage model from Session 3?
- Does the assertion improvement plan use the assertion ladder from Session 2?
- Does the triage playbook follow the decision tree structure from Session 4?
- Does the security review cover OWASP categories from Session 5?
- Are all decisions expressed in proper HTTP/API terminology from Session 0?
- Are GenAI-specific concepts (non-determinism, tokens, structured output) applied correctly from Session 1?

---

## Final Deliverable: Complete Test Plan

Your capstone test plan incorporates everything from the course:

| Component | Source Session | What It Contains |
|---|---|---|
| Coverage matrix | Session 3 | All test cases mapped to six axes, prioritized, and tiered |
| Assertion specifications | Session 2 | Detailed assertions at all 5 levels of the ladder |
| Triage playbook | Session 4 | Customized decision tree with ShopSmart-specific guidance |
| Security test cases | Session 5 | Prompt injection, PII, tool abuse, and environment security |
| HTTP/API foundations | Session 0 | Correct use of status codes, headers, and error handling |
| GenAI-specific coverage | Session 1 | Non-determinism handling, mode coverage, token awareness |

This plan is the kind of document you would present to a team lead on your first week in a real GenAI API testing role. Keep it practical, keep it prioritized, and keep it grounded in the frameworks you have learned.
