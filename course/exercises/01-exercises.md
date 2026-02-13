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

> **Solutions:** See `solutions/01-solutions.md` (instructor only).
