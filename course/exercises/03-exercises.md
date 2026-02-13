# Session 3 Exercises: Coverage Model

---

## Exercise 1: Coverage Matrix Builder (20 min)

### Setup

You are testing the ChatAssist API for a customer support chatbot called "ShopSmart Support." The system uses three of the four ChatAssist modes:

- **Chat completion** for general customer inquiries (return policy questions, product recommendations, complaint handling)
- **Structured output** for ticket classification -- every customer message is classified into one of five categories (`returns`, `shipping`, `billing`, `product_info`, `other`) with a confidence score
- **Tool calling** for order lookup (`lookup_order`) and inventory checks (`check_inventory`)

The system runs on `chatassist-4` with `temperature: 0.3` and `safety.level: "standard"`. The system prompt includes ShopSmart's return policy (30 days, original condition required) and tone guidelines ("friendly, professional, concise").

### Task

**Part A: Build the matrix (15 min)**

Create a coverage matrix with at least 20 test cases. For each test case, specify:

| Column | What to Write |
|---|---|
| Test ID | A short identifier (e.g., TC-01) |
| Axis | Which of the six axes does this test cover? (Input, Response Mode, Output Contract, Safety, Failure, Non-Functional) |
| Mode | Which ChatAssist mode? (Completion, Structured, Tool Calling, or All) |
| Scenario | One-sentence description of what the test does |
| Priority | P0, P1, P2, or P3 |
| Assertion Level | L1 Structural, L2 Containment, L3 Similarity, L4 LLM-as-judge, or L5 Statistical |
| Tier | Fast, Standard, or Deep |
| Est. Cost | Low, Medium, or High (based on expected token consumption) |

**Part B: Tier assignment (3 min)**

Count how many of your test cases fall into each tier. Does the distribution look right?

- Fast tier: should be your largest group (quick, cheap, high-value checks)
- Standard tier: medium-sized (more nuanced checks that take longer)
- Deep tier: smallest group (expensive, thorough evaluations)

If most of your tests are in the Deep tier, reconsider whether some can be simplified to run faster.

**Part C: Top 3 for CI/CD (2 min)**

Identify the 3 test cases you would add to the CI/CD pipeline first. For each, write one sentence explaining why it earns a spot in the fast tier.

### Hints

Think about these scenarios as you build your matrix:

- What happens when a customer asks about a product that does not exist?
- What happens when the model needs to call `lookup_order` but the customer did not provide an order number?
- What happens when the ticket classifier returns a confidence score below 0.5?
- What happens when someone tries to get the model to reveal the system prompt?
- What happens when you send the same classification request 5 times?
- What happens when the model's response mentions a return policy detail that is not in the system prompt (hallucination)?

---

## Exercise 2: Coverage Audit (Optional, 10 min)

### Setup

A colleague hands you the following list of 10 tests that already exist for the ShopSmart Support system:

1. Send "Hello" -- check status 200
2. Send "What is your return policy?" -- check response contains "30 days"
3. Send invalid API key -- check status 401
4. Send ticket classification request -- check response parses as valid JSON
5. Send ticket classification request -- check `sentiment` field exists
6. Send "Where is my order #12345?" -- check model calls `lookup_order`
7. Send tool result for order #12345 -- check final response mentions tracking number
8. Send empty messages array -- check status 400
9. Send request with `temperature: 5.0` -- check status 400
10. Check that `usage.total_tokens` is greater than 0 for a successful request

### Task

**Part A: Axis mapping**

For each of the 10 tests, identify which of the six coverage axes it addresses.

**Part B: Gap analysis**

Using the six-axis coverage map, identify at least 5 gaps in this test suite. For each gap, write:
- Which axis is underrepresented
- A specific test case that would fill the gap
- What priority (P0-P3) the new test should have

**Part C: The one test you would add first**

Pick the single most important missing test and justify your choice in 2-3 sentences. Consider: what failure in production would cause the most damage to ShopSmart's customers?

### Discussion Points

After completing the audit, consider:
- Did the existing tests skew toward any particular axis?
- Are there any axes with zero coverage?
- How would your prioritization change if ShopSmart handled financial transactions through the chatbot?

---

> **Solutions:** See `solutions/03-solutions.md` (instructor only).
