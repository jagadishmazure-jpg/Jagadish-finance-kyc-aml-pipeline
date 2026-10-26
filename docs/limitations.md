# Limitations and known failures

Kept visible on purpose. Each item below is either a test or a
documented gap, not a footnote to be discovered later.

1. **Matcher coverage is narrow.** The variant table covers a handful
   of given names. A name outside it, or a name written in a script
   the normalizer does not handle, can be missed. There is no recall
   measurement here because there is no labelled real dataset, and
   inventing one would be misleading.
2. **Short names over-match.** Two short, similar names can score
   above the review threshold and escalate a clean customer. That is
   the safe direction (a human looks), but it costs reviewer time.
3. **Risk bands are placeholders.** The band is a small rule set, not
   a calibrated model. It must not be quoted as a risk score.
4. **Audit log is in-memory.** Restarting loses the log. Persistence
   with append-only storage is planned, not present.
5. **No identity proofing.** "Identity verification" here means the
   synthetic record is complete. Real document checks, liveness, and
   registry lookups are entirely absent.
6. **Threshold is a guess.** 0.75 was picked as a starting point, not
   tuned. Tuning needs labelled pairs this repo deliberately does not
   fabricate into a claim.
7. **SQLite authorizer is per-connection.** A connection created
   without `create_store`/`create_seeded_store` has no authorizer.
   Adopters must route all access through those constructors.

## Known failure found during this build (fixed, test kept)

An escalated sanctions step once blocked the rest of the chain with a
dependency error, and per-customer state leaked across customers in
the demo. Both are now regression tests:
`test_escalated_step_still_satisfies_later_dependencies` and
`test_second_customer_not_contaminated_by_first_escalation`.
