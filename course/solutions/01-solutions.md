# Session 1 Solutions: Mode Matcher

> These are the solution notes for the Session 1 exercises. Do not distribute to participants before the session.

---

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
