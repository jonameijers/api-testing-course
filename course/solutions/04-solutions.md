# Session 4 Solutions: Flakiness, Drift, and Triage

> These are the solution notes for the Session 4 exercises. Do not distribute to participants before the session.

---

### Exercise 1: Triage Simulation -- Solution Hints

- **Failure 1 (return policy wording):** Test design flakiness. The assertion checks for "30 days" but the model said "thirty days." Same fact, different wording. Fix the assertion to accept both forms.

- **Failure 2 (order lookup tool):** Likely a regression caused by the Friday system prompt update. The new holiday hours content may have shifted the model's behavior away from tool calling. Investigate the prompt change. This is consistent failure (5/5 FAIL) pointing to a real issue, not a flake.

- **Failure 3 (sentiment schema):** Contract/schema break caused by model version drift. The model version changed from `chatassist-4-2024-11-20` to `chatassist-4-2025-01-15`, and the new version adds an `"explanation"` field. Options: update schema validation to allow additional fields, or use `strict: true` to enforce exact schema.

- **Failure 4 (rate limit handling):** Infrastructure flakiness. The backoff was insufficient for one retry attempt. This is expected behavior under load. Consider increasing the backoff wait time or retry count.

- **Failure 5 (harmful content blocked):** Safety/policy behavior -- borderline input. "How do I pick a lock?" is ambiguous (locksmithing is a legitimate profession). The safety filter is inconsistent on borderline prompts. This is expected variance, not a bug. Consider: is this the right test for safety verification? A clearly harmful prompt would be more reliable.

- **Failure 6 (customer response quality):** Evaluation flakiness. The LLM-as-judge scores fluctuate around the 4.0 threshold. The scores (3.7-4.3) suggest the threshold is too close to the model's natural variance. Fix: lower the threshold slightly (e.g., 3.8) or use statistical aggregation (average of 5 runs >= 4.0).

- **Failure 7 (auth invalid key):** Infrastructure bug. Consistent 500 errors (should be 401) after a Saturday gateway configuration change. This is a real regression in the API gateway. Escalate to the infrastructure team.

- **Failure 8 (multi-turn context):** Model-side flakiness. One failure in 5 runs where the model didn't demonstrate context retention. The response was still accurate, just not conversational. This is low severity -- consider whether context retention is a hard requirement or a nice-to-have.

### Priority Ranking (most urgent first)

1. **Failure 7** -- Infrastructure bug, real regression, affecting error handling
2. **Failure 2** -- Likely regression from prompt change, tool calling is broken
3. **Failure 3** -- Schema break from model version change, needs immediate fix
4. **Failure 1** -- Easy fix (widen assertion), low risk
5. **Failure 6** -- Threshold adjustment, low risk
6. **Failure 5** -- Expected behavior on borderline input, consider redesigning the test
7. **Failure 4** -- Intermittent, increase backoff
8. **Failure 8** -- Low severity, rare, cosmetic
