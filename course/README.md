# Testing GenAI APIs: A Course for UI Automation Testers

## Goal

Equip experienced UI automation testers with the concepts, vocabulary, and practical techniques needed to design, write, and maintain tests for Generative AI APIs — confidently and from day one.

## Target Audience

You are a **UI automation tester** (Selenium, Cypress, Playwright, or similar) who already knows how to:

- Write and maintain automated test suites
- Work with HTML selectors, page objects, and assertions
- Debug flaky tests and reason about test stability
- Read JSON and make sense of API responses

You may have **limited experience** with:

- Testing APIs directly (outside of UI-driven flows)
- HTTP fundamentals beyond what your framework abstracts away
- Large Language Models, prompt engineering, or GenAI-specific behavior

This course bridges that gap.

## Prerequisites

| Assumed | Not Required |
|---------|--------------|
| UI automation experience (1+ year) | Prior API testing experience |
| Basic JSON literacy | Knowledge of LLMs or GenAI |
| Comfort reading code (any language) | Specific programming language mastery |
| Familiarity with test assertions | Experience with HTTP clients like Postman or cURL |

## Course Schedule

The course consists of **6 sessions plus a capstone**, each approximately **90 minutes**.

| Session | Title | Focus |
|---------|-------|-------|
| **0** | HTTP & API Fundamentals | Requests, responses, status codes, headers, authentication — the foundation everything else builds on |
| **1** | How GenAI APIs Differ from Normal APIs | Non-determinism, token-based I/O, model parameters, streaming, structured output, tool calling |
| **2** | The Assertion Ladder | From exact match to semantic similarity — choosing the right assertion strength for GenAI responses |
| **3** | Coverage Model | What to test, what to skip, and how to think about coverage when outputs are unpredictable |
| **4** | Flakiness, Drift, and Triage | Why GenAI tests break, how to tell signal from noise, and building resilient test suites |
| **5** | Security and Responsible Testing | Prompt injection, PII leakage, safety filters, and ethical considerations for GenAI testing |
| **Capstone** | Put It All Together | Design a full test plan for the fictional ChatAssist API, applying every concept from the course |

## Format

Each session follows the same structure:

1. **Bridge from UI Testing** (10 min) — connects the new topic to something you already know from UI automation
2. **Concept introduction** (25 min) — the core ideas, explained with examples
3. **Worked examples** (20 min) — walk through realistic scenarios using the fictional ChatAssist API
4. **Discussion and Q&A** (15 min) — clarify, debate, and connect to real-world experience
5. **Paper exercise** (20 min) — a hands-on activity completed on paper or whiteboard (no tooling required)

**Key design choices:**

- **Concept-first**: We teach the "why" and "what" before the "how." Tools change; principles don't.
- **Tool-agnostic**: Examples use generic HTTP and JSON. No vendor lock-in, no specific test framework.
- **Paper exercises**: Deliberately low-tech. The goal is thinking, not typing.
- **Shared reference docs**: Every session produces a tangible artifact the team can use after the course.

## Deliverable Artifacts

Each session produces a reference document that becomes part of the team's shared testing library:

| Artifact | Produced In | Description |
|----------|-------------|-------------|
| **UI-to-API Bridge Reference** | All sessions | Running comparison of UI testing concepts and their API/GenAI equivalents |
| **HTTP & API Cheat Sheet** | Session 0 | Quick reference for methods, status codes, headers, and authentication patterns |
| **Assertion Strength Guide** | Session 2 | Decision framework for choosing assertion types for GenAI responses |
| **Coverage Matrix Template** | Session 3 | Spreadsheet-style template for mapping GenAI API test coverage |
| **Triage Decision Tree** | Session 4 | Flowchart for diagnosing whether a test failure is flakiness, drift, or a real bug |
| **Security Testing Checklist** | Session 5 | Checklist of security and responsibility considerations for GenAI API testing |

## The "Bridge from UI Testing" Concept

Every session opens with a **Bridge from UI Testing** segment. This is the single most important pedagogical choice in the course.

**The idea:** You already have deep testing intuition built from years of UI automation. GenAI API testing is not a completely new discipline — it is an evolution of skills you already have. The Bridge segment makes this connection explicit.

**How it works:**

- We take a concept you know well from UI testing (e.g., "a flaky test that passes sometimes and fails sometimes")
- We show the direct parallel in GenAI API testing (e.g., "a non-deterministic response that varies across identical requests")
- We highlight what's the same (debugging instincts, isolation strategies) and what's different (the source of variation, the assertion approach)

**Example bridges:**

| UI Testing Concept | GenAI API Parallel |
|---|---|
| A Selenium selector that breaks when the DOM changes | A JSON path assertion that breaks when the model output format drifts |
| A visual regression test with a pixel-diff threshold | A semantic similarity assertion with a cosine-similarity threshold |
| Waiting for a page to load before asserting | Waiting for a streaming response to complete before validating |
| Testing that a button is disabled for unauthorized users | Testing that an API returns 401 for invalid API keys |
| Flaky tests caused by animation timing | Flaky tests caused by non-deterministic model output |

This approach reduces cognitive load, builds confidence, and helps testers transfer existing expertise rather than starting from scratch.

## How to Use This Material

### Instructor-Led (Recommended)

- Run one session per week (or per sprint)
- Allocate 90 minutes per session
- Use the paper exercises as group activities
- Build the deliverable artifacts collaboratively
- Use the ChatAssist API spec as a shared reference throughout

### Self-Paced

- Work through sessions in order (each builds on the previous)
- Complete paper exercises individually, then review the provided solution notes
- Build your own versions of the deliverable artifacts
- Revisit the Bridge segments whenever you need to reconnect new concepts to familiar ground

### As a Reference

- Use the glossary for quick term lookups
- Use the deliverable artifacts as templates for real projects
- Use the ChatAssist API spec as a model for documenting your own GenAI API under test

## The ChatAssist API

All examples in this course use a fictional API called **ChatAssist**. It is a realistic, vendor-neutral GenAI API that supports:

- Chat completions (text in, text out)
- Structured output (JSON schema enforcement)
- Tool/function calling
- Streaming (Server-Sent Events)
- Safety and moderation settings

See [examples/fictional-test-suite/chatassist-api-spec.md](examples/fictional-test-suite/chatassist-api-spec.md) for the full specification.

ChatAssist is intentionally fictional so that:

1. Examples never go stale when a real vendor changes their API
2. We can design the API to illustrate exactly the testing challenges we want to teach
3. Learners focus on testing principles rather than vendor-specific quirks

## Repository Structure

```
course/
  README.md                  -- This file
  glossary.md                -- Alphabetized term definitions
  session-briefs.md          -- Detailed outlines for each session
  sessions/                  -- Full session content
  exercises/                 -- Paper exercises and solution notes
  artifacts/                 -- Deliverable templates
  examples/
    fictional-test-suite/    -- ChatAssist API spec and example tests
    pseudo-api-responses/    -- Realistic API response samples
    pseudo-logs/             -- Simulated CI and test logs
```
