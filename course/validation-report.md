# Course Validation Report

> Validated: February 2026
> Validator: Researcher agent
> Scope: All course content validated against research briefs (research-brief-practices.md, research-brief-challenges.md)

---

## Executive Summary

The course content is **strong overall**. All seven sessions, seven exercises, six artifacts, example files, and the glossary were reviewed against current research findings. The course accurately represents 2025-2026 best practices, correctly aligns with the OWASP Top 10 for LLM Applications 2025, and maintains consistent references to the fictional ChatAssist API throughout.

**Verdict: PASS with minor recommendations.**

Below are detailed findings across the seven validation dimensions.

---

## 1. Accuracy of Best Practices

**Rating: Strong**

The course accurately represents current best practices in GenAI API testing. Specific verification points:

### Confirmed Accurate

- **Assertion ladder (Session 2)**: The five-level ladder (Structural, Containment, Similarity, LLM-as-Judge, Statistical) matches the research consensus from Promptfoo, Langfuse, and Evidently AI. The progression from deterministic to non-deterministic is correctly presented.

- **LLM-as-Judge best practices (Session 2)**: All 8 guidelines are research-supported:
  1. Explicit score definitions -- confirmed (Evidently AI, Monte Carlo Data)
  2. Split complex criteria into separate evaluators -- confirmed (Confident AI)
  3. Chain-of-thought reasoning -- confirmed (Patronus, Evidently AI)
  4. Few-shot examples -- confirmed (Monte Carlo Data)
  5. Judge temperature to 0 -- confirmed (Evidently AI)
  6. Cohen's kappa > 0.8 calibration -- confirmed (Evidently AI, research standards)
  7. Self-consistency checks -- confirmed (Langfuse)
  8. Watch for biases (verbosity, position) -- confirmed (Evidently AI)

- **Tiered CI/CD strategy (Session 3)**: The Fast/Standard/Deep tier model matches industry patterns documented by Promptfoo, Arize AI, Deepchecks, and Braintrust. Tier definitions and criteria align with research.

- **Four categories of flakiness (Session 4)**: Model-side, Infrastructure, Test Design, and Evaluation flakiness categories match the research taxonomy from GenAI Days, Stack Overflow, and Awesome Testing sources.

- **Continuous feedback loop (Session 4)**: The Deploy-Observe-Identify-Add-Fix-Redeploy cycle is accurately represented and sourced. This is identified as the "single most important pattern" in both the research and the course.

- **Model drift detection strategies (Session 4)**: Version pinning, periodic evaluations, canary test suites, and score tracking over time are all research-validated approaches.

- **Cost-aware test design (Session 3)**: Token budgets, caching, model routing, LLM-as-judge cost doubling, and hidden token categories (reasoning, failed request, agentic) are accurately presented.

### Minor Observations

- **Structured Outputs achieving "100% schema conformance"** (Session 2, line 115): This claim references OpenAI's Structured Outputs feature. The course correctly presents this with the ChatAssist `strict: true` parameter. While the claim is accurate for OpenAI's implementation, it is worth noting this is vendor-specific behavior and not universal across all GenAI APIs. The course handles this adequately by framing it within the ChatAssist context.

- **The evaluation framework landscape** (research-brief-practices.md Section 2): The course does not dedicate a standalone section to evaluation framework tools (RAGAS, DeepEval, Promptfoo, LangSmith, etc.), which is appropriate for the target audience. These are implementation tools rather than conceptual frameworks, and the course correctly focuses on the underlying patterns (assertion ladder, coverage model) rather than specific tool names. **No change needed** -- this is a deliberate and appropriate scoping decision for UI testers who need concepts, not tool-specific training.

---

## 2. Completeness vs. Research Findings

**Rating: Good, with minor gaps**

### Well Covered

- Non-determinism and its testing implications
- All four modes of GenAI API operation (completion, structured output, tool calling, streaming)
- Model versioning and drift (with real-world examples)
- Prompt injection (direct and indirect, with five technique categories)
- PII leakage (input-side, output-side, storage-side)
- Cost management and token budgeting
- Rate limiting and retry strategies
- The assertion spectrum from deterministic to probabilistic
- Security vulnerability patterns (all 8 recurring patterns)
- Regulatory context (EU AI Act, ISO standards, NIST)

### Minor Gaps (Consider for Future Updates)

1. **RAG pipeline testing**: The research brief covers RAG testing in depth (retriever evaluation, generator evaluation, faithfulness metrics, context poisoning). The course mentions RAG in the context of OWASP LLM08 (Vector and Embedding Weaknesses) and in the glossary, but does not provide a dedicated testing methodology for RAG pipelines. **Recommendation**: This is acceptable for the current scope. RAG testing could be a follow-up module or advanced topic. The ChatAssist API does not explicitly include a RAG mode, so excluding detailed RAG testing is consistent with the fictional scenario.

2. **Multi-modal testing**: The research brief covers vision, audio, and cross-modal testing patterns. The course mentions multimodal inputs briefly in Session 3 (Axis 1 -- Input Modality) and includes "Multimodal" in the glossary. **Recommendation**: Acceptable for current scope. The ChatAssist API is text-focused. Multi-modal testing could be a future extension module.

3. **Agent testing beyond tool calling**: The research covers multi-step agent workflows, infinite loops, false completion claims, and instruction drift in agent systems. The course covers tool calling testing well but does not address autonomous agent evaluation patterns (multi-step planning, task completion metrics). **Recommendation**: The course's focus on tool calling is appropriate for the target audience (UI testers starting with GenAI APIs). Multi-step agent evaluation is an advanced topic that goes beyond the introductory scope.

4. **Human-in-the-loop evaluation**: Research identifies A/B testing with human raters and user surveys as foundational for subjective quality. The course mentions "human review" in the Deep tier and "calibrate against human labels" for LLM-as-judge, but does not dedicate a section to human evaluation workflows. **Recommendation**: Minor gap. The course correctly positions human review as part of the Deep tier. No dedicated section is needed for this introductory course.

5. **Data exfiltration via markdown image injection**: The research brief describes this specific technique (LLM outputs an image tag with exfiltrated data as URL parameters). Session 5 mentions the general concept in the "Real-World Incidents" section but does not include a specific test case for markdown image injection. **Recommendation**: Consider adding a brief test case example to the prompt injection section of Session 5 or the security exercises. This is a practical, demonstrable attack pattern.

---

## 3. Currency of Examples and References

**Rating: Strong**

### Current and Accurate

- **OWASP Top 10 for LLM Applications 2025**: Correctly referenced throughout Session 5. All 10 categories match the official 2025 list. Key changes from 2023 to 2025 are accurately described (LLM08 new, LLM07 elevated, LLM10 renamed).

- **Real-world drift examples (Session 4)**:
  - GPT-4o default update (October 2024) -- confirmed accurate
  - GPT-4o structure regression (late 2024) -- confirmed accurate
  - GPT-4.5 deprecation (April 2025) -- confirmed accurate

- **Real-world security incidents (Session 5)**:
  - Slack AI vulnerability (2024) -- confirmed accurate
  - ServiceNow agent privilege escalation (late 2025) -- confirmed accurate
  - Markdown image injection data exfiltration -- confirmed accurate

- **Regulatory references**:
  - EU AI Act (effective 2025-2026) -- correctly described
  - ISO/IEC TS 42119-2:2025 -- correctly described as first AI testing standard
  - ISO/IEC 42001:2023 -- correctly described
  - NIST AI RMF -- correctly described

- **Research statistics (Session 5)**:
  - "22% of files uploaded to AI tools contain sensitive content" -- matches Harmonic Security report
  - "32% of sensitive data leaked is source code" -- matches Harmonic Security report
  - "$9.36 million average GenAI breach cost" -- matches Wald.ai analysis

### Date Sensitivity

- The course content uses 2024-2025 examples, which are current as of the February 2026 validation date. No outdated advice was found.
- The ChatAssist API specification uses dates in 2024 for its example model versions (e.g., `chatassist-4-2024-08-06`), which is appropriate for a fictional API.
- The CI failure logs use February 2024 dates, which works as a teaching scenario regardless of the actual date.

---

## 4. OWASP Alignment (Session 5)

**Rating: Excellent**

Session 5 provides comprehensive coverage of the OWASP Top 10 for LLM Applications 2025:

| OWASP Category | Course Coverage | Assessment |
|---|---|---|
| LLM01: Prompt Injection | Full section (Section 2) with 5 direct techniques, indirect scenarios, real incidents, and ChatAssist test examples | Excellent |
| LLM02: Sensitive Info Disclosure | Full section (Section 3) covering input/output/storage PII risks with ChatAssist test scenarios | Excellent |
| LLM03: Supply Chain | Mentioned with appropriate note that it is less directly testable at API level | Adequate |
| LLM04: Data Poisoning | Mentioned with appropriate note about relevance to fine-tuning pipelines | Adequate |
| LLM05: Improper Output Handling | Covered with ChatAssist test scenario for HTML/script injection | Good |
| LLM06: Excessive Agency | Covered with ChatAssist tool boundary test example | Good |
| LLM07: System Prompt Leakage | Covered in both Section 2 (extraction techniques) and the security checklist | Good |
| LLM08: Vector/Embedding Weaknesses | Mentioned as new in 2025, with note about RAG pipeline relevance | Adequate |
| LLM09: Misinformation | Covered with ChatAssist hallucination test scenario | Good |
| LLM10: Unbounded Consumption | Covered with context window limit test scenario | Good |

The security checklist deliverable at the end of Session 5 correctly maps test cases to OWASP categories. The changes from 2023 to 2025 are accurately described.

**Key strength**: The "prompt injection is the SQL injection of the AI era" analogy in the Session 5 bridge section is an excellent teaching device for UI automation testers. This parallel is supported by the research.

---

## 5. Practical Relevance of Exercises

**Rating: Strong**

### Exercise Quality Assessment

| Exercise | Realism | Skill Transfer | Assessment |
|---|---|---|---|
| 00: HTTP Decoder | High -- real-world request/response pairs with GenAI-specific headers | Bridges existing HTTP knowledge | Excellent |
| 01: Mode Matcher | High -- scenarios match real application patterns | Builds mode identification skills | Excellent |
| 02: Assertion Level Selector | High -- 10 scenarios spanning all assertion levels | Develops assertion judgment | Excellent |
| 03: Coverage Matrix Builder + Audit | High -- uses ChatAssist API with realistic gaps | Develops audit instincts | Excellent |
| 04: Triage Simulation | High -- 8 realistic failure scenarios with ambiguity | Develops triage judgment | Excellent |
| 05: Security Test Designer | High -- OWASP-mapped scenarios with ChatAssist context | Develops security testing skills | Excellent |
| 06: Capstone (ShopSmart) | Excellent -- comprehensive scenario with realistic system prompt, 15 existing tests, 4 known issues, CI logs | Integrates all course skills | Excellent |

### Capstone Scenario Validation

The ShopSmart capstone brief is particularly well-designed:

- **Realistic system prompt**: Contains actual policy details, escalation rules, and internal routing information -- creating natural targets for security testing.
- **Known issues reflect real-world patterns**: The "thirty days" vs. "30 days" issue is a classic model-side flakiness pattern. The tool calling flakiness is a documented real-world problem. The hallucinated electronics policy is a realistic grounding failure. The CI streaming timeout is a common infrastructure issue.
- **CI failure log**: The 7-day log with realistic failure patterns and pass rates (94.3%) gives learners authentic data to analyze.
- **Pseudo-logs**: Both `ci-run-flaky.log` and `ci-run-regression.log` are exceptionally well-crafted, showing realistic test output with timing, token counts, similarity scores, retries, and analysis notes. These demonstrate exactly what learners would see in a real CI pipeline.

### One Enhancement Suggestion

- The exercises are all paper-based (designed for discussion and analysis, not coding). This is noted in the README and is appropriate for the 90-minute session format. **For a potential hands-on extension**, the pseudo-API responses and CI logs could be adapted into interactive exercises where learners write assertions against the example JSON files.

---

## 6. Consistency of ChatAssist API References

**Rating: Excellent**

The fictional ChatAssist API is used consistently across all course materials:

### API Specification Consistency

| Element | API Spec | Sessions | Exercises | Examples | Consistent? |
|---|---|---|---|---|---|
| Model names | chatassist-4, chatassist-4-mini, chatassist-3 | Correct throughout | Correct | Correct | Yes |
| Endpoint | POST /v1/chat/completions | Correct throughout | Correct | Correct | Yes |
| Auth format | Bearer ca-key-{id} | Correct throughout | Correct | Correct | Yes |
| Rate limit tiers | Free (10/min), Standard (60/min), Enterprise (600/min) | Correct throughout | Correct | Correct | Yes |
| Safety levels | strict, standard, minimal | Correct throughout | Correct | Correct | Yes |
| Safety categories | 6 categories | Correct throughout | Correct | Correct | Yes |
| Context window | 128K (chatassist-4), 32K (mini), 16K (chatassist-3) | Correct | Correct | N/A | Yes |
| Finish reasons | stop, length, tool_calls, safety | Correct throughout | Correct | Correct | Yes |
| Temperature range | 0.0-2.0 | Correct | Correct | Correct | Yes |
| Structured output | strict: true, response_format with json_schema | Correct | Correct | Correct | Yes |
| Tool calling | tools array with function definitions | Correct | Correct | Correct | Yes |
| Streaming | stream: true, SSE format, [DONE] signal | Correct | Correct | Correct | Yes |

### Cross-Reference Check

- The ShopSmart capstone uses `chatassist-4` with `temperature: 0.3`, which is consistent with the API spec's valid range and the system configuration described in the capstone brief.
- The tools defined in the capstone (`lookup_order`, `check_inventory`, `create_return`) are consistently described across the capstone exercise, session 6, and the capstone brief.
- Error codes in exercises match the API spec's error catalog (400, 401, 403, 429, 500, 503).
- The pseudo-API response examples (successful-completion.json, tool-call-response.json, safety-block.json) all use correct field names and structure matching the API spec.
- The pseudo-CI logs reference consistent model names, token counts, and assertion patterns.

**No inconsistencies found.**

---

## 7. Glossary Completeness

**Rating: Good, with minor additions recommended**

### Coverage Check

I checked all technical terms used in sessions against the glossary. The glossary contains approximately 40 terms and covers the vast majority of concepts.

### Terms Present and Well-Defined

API key, Assertion, Backoff, Bearer token, Caching, Completion, Context window, Embedding, Endpoint, Fine-tuning, Function calling (redirects to Tool calling), Grounding, Hallucination, Header, HTTP methods, Idempotency, JSON, JSON Schema, Latency, max_tokens, Model version, Multimodal, Non-deterministic, OAuth, PII, Prompt, Prompt injection, RAG, Rate limit, Request/Response, REST, Retry, Safety filter, Schema adherence, Schema validation, SSE, Status code, Streaming, Structured output, Temperature, Token, Tokenization, Tool calling, top_p, Transport layer, TTL, Webhook.

### Terms Used in Course but Missing from Glossary

1. **Cosine similarity** -- Used extensively in Sessions 2, 3, and in the pseudo-CI logs. The glossary mentions "embedding" but does not define cosine similarity as a standalone term. **Recommendation: Add.**

2. **OWASP** -- Referenced throughout Session 5. While many learners may know OWASP from web security, it is worth defining for completeness. **Recommendation: Add.**

3. **Red teaming** -- Used in Session 3 (Deep tier), Session 4 (continuous feedback), Session 5 (regulatory context), and the research brief. Not defined in the glossary. **Recommendation: Add.**

4. **Drift (model drift)** -- Central concept in Session 4. "Model version" is in the glossary but "drift" as a standalone concept is not. **Recommendation: Add.**

5. **Circuit breaker** -- Used in Session 4 (infrastructure flakiness mitigations). A pattern from distributed systems that may be unfamiliar to UI testers. **Recommendation: Add.**

6. **Jitter** -- Used in Session 4 alongside exponential backoff. "Backoff" is defined but jitter is not. **Recommendation: Add a note to the Backoff entry or create a separate entry.**

7. **Cohen's kappa** -- Referenced in Session 2 (LLM-as-Judge best practices). A statistical measure that UI testers are unlikely to know. **Recommendation: Add.**

8. **Canary test** -- Used in Session 4 (drift detection). Not a standard term outside of deployment contexts. **Recommendation: Add.**

### Terms That Could Be Enhanced

- **Safety filter**: The definition mentions `finish_reason: "safety"` but does not mention `safety_metadata` which appears in the API spec and example responses. Minor enhancement.

---

## Summary of Recommendations

### Priority 1 (Address Before Launch)

None. The course is ready for use in its current state.

### Priority 2 (Minor Enhancements)

1. **Glossary additions**: Add definitions for cosine similarity, OWASP, red teaming, drift, circuit breaker, jitter, Cohen's kappa, and canary test. (Estimated effort: 30 minutes)

2. **Markdown image injection test case**: Consider adding a brief example to Session 5's prompt injection section demonstrating the markdown image exfiltration technique. This is a practical, well-documented attack pattern that would strengthen the security coverage. (Estimated effort: 15 minutes)

### Priority 3 (Future Consideration)

3. **RAG pipeline testing module**: Could be added as an optional Session 7 or advanced appendix for teams using retrieval-augmented generation.

4. **Multi-modal testing module**: Could be added when the ChatAssist API is extended to support image/audio inputs.

5. **Interactive exercise variants**: The pseudo-API responses and CI logs could be adapted into hands-on coding exercises for teams that want to go beyond the paper-based format.

---

## Conclusion

The course provides a comprehensive, accurate, and practical introduction to GenAI API testing for UI automation testers. It correctly applies current best practices from 2025-2026 research, maintains excellent internal consistency across all materials, and provides realistic exercises grounded in the well-designed ChatAssist API scenario. The OWASP alignment is excellent, and the regulatory context is appropriately scoped. The recommended enhancements are minor and do not affect the course's readiness for use.
