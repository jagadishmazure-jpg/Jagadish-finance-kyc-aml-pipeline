# How it works, step by step

1. **Load a synthetic record.** `demo.py` reads
   `data/synthetic_customers.json` and the synthetic lists. No
   network call happens at any point.
2. **Identity.** The chain checks the record carries an identity
   document type. An empty type fails the chain to human review.
3. **Sanctions.** The name is normalized (lower-cased, de-accented,
   punctuation stripped), spelling variants are generated, and the
   best fuzzy score against each synthetic list entry is computed.
   A score at or above 0.75 is a hit.
4. **PEP.** The same matcher runs against the synthetic PEP list.
   A transliteration variant (for example, one spelling of a name
   matching another) scores high and escalates.
5. **Risk.** The band comes from grounded facts only: a high-risk
   country raises the band; an escalated screening raises it to
   medium. No step reads another step's prose.
6. **Decision.** If anything escalated or failed, the outcome is
   `human_review` and a dry-run notice is recorded. Otherwise the
   outcome is `approve`.
7. **Audit.** Every step and the final decision append a redacted
   entry to the hash chain. `audit.verify()` recomputes the chain;
   any tampered or deleted entry makes it return False.
8. **Release.** A reviewer releases an escalated case only through
   `ConfirmationGate` with a clean "yes" and a valid approval
   (named approver, correct scope, unexpired, unused). The approval
   is consumed on use.

## Why an escalated step does not block the chain

Early in this build, an escalated sanctions step blocked PEP with a
dependency error, so a fuzzy hit was reported as a chain failure
instead of a human review. The fix: a step with status `escalated`
satisfies later dependencies, because it ran and produced a result.
Only a missing or failed step blocks. This is covered by
`test_escalated_step_still_satisfies_later_dependencies` and
`test_second_customer_not_contaminated_by_first_escalation`.
