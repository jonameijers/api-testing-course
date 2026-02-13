# Session 1 Exercises: Mode Matcher

**Duration:** 20 minutes
**Format:** Paper-based (no tools required)

---

## Setup

Below are eight scenarios describing how an application uses a GenAI API. For each scenario, you will identify the appropriate mode, parameters, and testing challenges.

---

## Scenarios

### Scenario 1: Ticket Classifier

A support system receives customer emails and needs to classify each one into exactly one category: `billing`, `shipping`, `returns`, `product_info`, or `other`. The classification must include a confidence score. The result is stored in a database for routing.

### Scenario 2: Live Chat

A customer-facing chatbot on an e-commerce website responds to customer questions in real time. Customers see the response appear word by word as it is generated. The chatbot should be conversational and helpful.

### Scenario 3: Order Status Lookup

A customer asks "Where is my order #98765?" The system needs to look up the actual order in a database and provide real shipping information (carrier, tracking number, estimated delivery).

### Scenario 4: Product Description Writer

A marketing tool generates creative product descriptions from a list of features. Each description should be unique and engaging. The team wants variety -- different descriptions for the same product each time.

### Scenario 5: Safety Report Summarizer

A compliance tool reads incident reports (each up to 50 pages) and produces a one-paragraph summary. Accuracy is critical. The summary must not add any information that is not in the original report.

### Scenario 6: FAQ Response

A website widget answers common questions about the company's return policy. The answers should be consistent -- every customer should receive essentially the same information about the 30-day return window.

### Scenario 7: Multi-step Research Assistant

A research tool helps analysts answer complex questions. It can search a knowledge base, query a financial data API, and read company filings. It decides which sources to use based on the question, and may need to make multiple queries before producing an answer.

### Scenario 8: Sentiment Dashboard

An analytics system processes thousands of customer reviews per hour and displays a real-time dashboard showing sentiment trends. Each review must produce a structured result with sentiment label, score, and detected topics.

---

## Tasks

### Task 1: Mode Selection

For each scenario, identify which ChatAssist mode to use and justify your choice:

| Scenario | Mode | Justification |
|----------|------|---------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |

Modes to choose from: **Chat Completion**, **Structured Output**, **Tool Calling**, **Streaming**

### Task 2: Parameter Tuning

For each scenario, identify one parameter you would set differently from the default, and explain why:

| Scenario | Parameter | Value | Why |
|----------|-----------|-------|-----|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |

### Task 3: Sketch the Request

For **two** scenarios of your choice, sketch the key fields of the request body. You do not need full JSON -- just list the fields and their purpose.

Example sketch:
```
model: chatassist-4
messages: [system message setting role, user message with the input]
temperature: 0.0
response_format: json_schema with fields X, Y, Z
```

### Task 4: Assertion Difficulty

Rank all eight scenarios from easiest to hardest to assert on. For the top 3 hardest, explain what makes them difficult.

---

## Solution Notes

### Task 1: Mode Selection

| Scenario | Mode | Justification |
|----------|------|---------------|
| 1 | **Structured Output** | Needs a specific JSON structure (category enum + confidence score) for database storage. `strict: true` ensures valid output. |
| 2 | **Streaming** | Live chat requires word-by-word delivery to reduce perceived latency. |
| 3 | **Tool Calling** | Must query a real database. The model cannot know order status on its own -- it needs the `lookup_order` tool. |
| 4 | **Chat Completion** | Creative text generation with no structural constraints. Variety is desired. |
| 5 | **Chat Completion** | Free-form summary. Could use Structured Output if a fixed format is needed, but a paragraph summary is best as plain text. |
| 6 | **Chat Completion** | Simple Q&A. Structured Output would be overkill for a text response. Low temperature ensures consistency. |
| 7 | **Tool Calling** | Must access multiple external data sources. The model decides which tools to use and in what order. |
| 8 | **Structured Output** | High volume requires machine-parseable output. Must produce consistent JSON with sentiment, score, and topics. |

### Task 2: Parameter Tuning

| Scenario | Parameter | Value | Why |
|----------|-----------|-------|-----|
| 1 | `temperature` | `0.0` | Classification should be deterministic, not creative |
| 2 | `max_tokens` | `500` | Limit response length for chat; avoid overly long replies |
| 3 | `tool_choice` | `"required"` | Force the model to use the lookup tool rather than guessing |
| 4 | `temperature` | `1.2 - 1.5` | High temperature produces creative variety |
| 5 | `temperature` | `0.0` | Accuracy is critical; minimize variation |
| 6 | `temperature` | `0.0 - 0.3` | Consistency is desired; every customer gets the same core facts |
| 7 | `max_tokens` | `2000` | Complex multi-source answers may require more space |
| 8 | `temperature` | `0.0` | High-volume automated processing needs deterministic results |

### Task 3

(Answers will vary. Key is that students identify the right top-level fields for their chosen mode.)

### Task 4: Assertion Difficulty Ranking (easiest to hardest)

1. **Scenario 1 (Ticket Classifier)** -- Structured Output with an enum; fully deterministic format
2. **Scenario 8 (Sentiment Dashboard)** -- Structured Output at volume; format is fixed
3. **Scenario 3 (Order Status)** -- Tool call is deterministic; final answer should contain factual data from the tool
4. **Scenario 6 (FAQ Response)** -- Low temperature, known facts; can assert on key terms
5. **Scenario 5 (Safety Report)** -- Must verify nothing was added; requires faithfulness checking
6. **Scenario 2 (Live Chat)** -- Streaming adds complexity; conversational output is hard to pin down
7. **Scenario 7 (Research Assistant)** -- Multi-step, multi-tool; many branching paths to verify
8. **Scenario 4 (Product Description)** -- Intentionally creative and varied; hardest to define "correct"

**Why the top 3 are hardest:**

- **Scenario 4:** The goal is *variety*, so any fixed assertion would fight the purpose. You can check for relevance to the product features but not for specific wording.
- **Scenario 7:** Multiple tools, multiple steps, branching logic. The model might take different paths to the same answer, making assertion on the process nearly impossible -- you can only assert on the final result quality.
- **Scenario 2:** Streaming means you must concatenate chunks before asserting. The conversational nature means responses will vary in tone, length, and phrasing even for the same question.
