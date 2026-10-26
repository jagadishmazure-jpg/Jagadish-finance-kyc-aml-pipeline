# Threat model

Scope: this scaffold only — synthetic data, in-memory store, no
network. A production system would need a much larger model.

| Threat (STRIDE-flavoured) | Mitigation here | Residual risk |
|---|---|---|
| Tampering with audit history | Hash chain; verification on read | In-memory log is lost on restart; no append-only store yet |
| Information disclosure via logs/errors | PII redaction incl. cards + emails; views hide PII columns | A new PII pattern not in the redactor could leak; add a pattern + test before adding a field |
| Elevation via self-approved release | Named, single-use, scoped, expiring approvals; gates fail closed | Approval issuance itself is out of scope — a weak issuer breaks the gate |
| Spoofing / wrong-person screening | Dependency order + re-grounding + drift check | Matcher can still confuse similar names; that is why hits escalate |
| Denial via unbounded reads | Fetch-time row cap (`fetchmany(MAX+1)`) | Cap is per call; a caller looping calls can still walk the table through views |
| Repudiation of a decision | Every step + decision is audit-logged with a hash | Log has no signer identity yet; add signing in a real system |
| Injection through names | Names are data, never SQL: all queries are fixed strings or parameters | Matcher input is not sanitized for display; escape on render in any UI |

## LLM-specific notes

This scaffold uses no language model: the "compounding hallucination"
risk from multi-step chains is addressed structurally (re-grounding
+ drift check) rather than by prompt engineering. If an LLM step is
added later, its output must be validated against the same grounded
facts before it can influence the decision, and its raw text must
never be stored in the audit log unredacted.
