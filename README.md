# KYC/AML Due-Diligence Pipeline — Tarnmoor Bank (fictional)

> **All data in this repo is SYNTHETIC.** Every customer, watchlist
> entry and document number is invented. Nothing here connects to a
> real sanctions list, a real regulator, or a real person. This is a
> portfolio demonstration of pipeline design, not a compliance product,
> and it makes no claim of meeting any regulation.
>
> **No affiliation claim:** this project is not affiliated with, or
> endorsed by, any university or training provider. The firm name
> "Tarnmoor Bank" is invented for this repo.

## Recruiter summary

- **Problem:** onboarding checks run as a chain (identity, watchlist
  screening, risk scoring, decision), and a small error early in the
  chain can quietly corrupt everything downstream — while auditors
  still need a tamper-evident record of every step.
- **Approach:** a dependency-ordered chain where each step re-reads
  its inputs from the source record, a drift check fails the chain on
  any contradiction, fuzzy screening escalates to a human instead of
  auto-rejecting, and every step lands in a hash-chained audit log.
- **Proof (real runs, this repo):** 80 tests pass with system
  `python3`/`pytest`; the offline demo over 4 synthetic customers
  returns 2 approvals and 2 human reviews, with a verified audit
  chain. These are regression checks on invented data, not quality or
  compliance claims.

## What it does

1. **Identity verification** — checks the synthetic record is complete
   before anything else runs.
2. **Sanctions screening** — fuzzy name matching against a synthetic
   list, including spelling variants and de-accented forms.
3. **PEP screening** — the same fuzzy matcher against a synthetic
   politically-exposed-persons list.
4. **Risk rating** — a band (low / medium / high) derived only from
   grounded facts, never from a previous step's free text.
5. **Decision** — approve, or escalate to a human reviewer. A fuzzy
   hit never auto-rejects on its own.

A step cannot run before its dependencies have run
(`tests/test_chain.py`: dependency tests). Each step re-grounds its
facts from the source record, and a drift check fails the chain when a
downstream step contradicts a verified upstream fact
(`test_drift_in_downstream_step_fails_chain`).

## Real output

From `PYTHONPATH=src python3 -m kyc_aml.demo` (4 synthetic customers):

```text
Tarnmoor Bank (fictional) -- KYC/AML demo, SYNTHETIC data only
CUST-001: approve (low) -- all steps passed, no hits
CUST-002: human_review (medium) -- fuzzy hit requires human review
CUST-003: human_review (medium) -- fuzzy hit requires human review
CUST-004: approve (high) -- all steps passed, no hits
audit entries: 24, chain valid: True
```

Fuzzy matching, real run:

```python
>>> screen_name("Mohammed Alar", [{"name": "Mohamed Alar"}], "synthetic-pep")
[{'list_name': 'synthetic-pep', 'matched_name': 'Mohamed Alar',
  'score': 0.96, 'variants_used': ['mohammed alar']}]
```

## How to run (offline first)

```bash
python3 -m pytest tests/ -q        # full suite, stdlib only
PYTHONPATH=src python3 -m kyc_aml.demo
```

No network, no keys, no services, no install step. Python 3.12 and
`pytest` are the only requirements. There is no deployment, no PyPI
package, and no CI badge in this scaffold.

## Guardrails (each one has a named proof test)

| Control | Proof test |
|---|---|
| View-only SQLite authorizer (base tables, `sqlite_master`, writes, PRAGMA, ATTACH denied) | `test_store_authorizer.py`: `test_direct_base_table_read_denied`, `test_sqlite_master_read_denied`, `test_insert_denied`, `test_pragma_denied`, `test_attach_denied` |
| Confirmation gates: bypass / reject / absent / low-confidence / contradicting consent | `test_gates.py`: `test_gate_bypass_without_approval_denied`, `test_gate_reject_on_explicit_no`, `test_gate_absent_empty_response_denied`, `test_gate_low_confidence_maybe_yes_denied`, `test_gate_contradicting_yes_wait_no_denied` |
| Approvals: named-person, single-use, scoped, expiring | `test_gate_approval_is_single_use`, `test_gate_expired_approval_denied`, `test_gate_wrong_scope_denied`, `test_gate_anonymous_approver_denied` |
| PII redaction incl. cards + emails | `test_redaction_audit_budget_notify_brand.py`: `test_card_number_redacted`, `test_email_address_redacted`, `test_safe_error_never_carries_card_or_email` |
| Row cap at fetch time (`fetchmany(MAX+1)`, no LIMIT rewriting, no `fetchall`) | `test_fetch_cases_row_cap_enforced_at_fetch_time`, `test_fetch_customers_row_cap_enforced` |
| Negative costs rejected | `test_negative_cost_rejected`, `test_negative_cost_add_rejected_and_spent_unchanged` |
| Non-empty brand blocklist (stored as hashes) | `test_brand_blocklist_is_non_empty`, `test_brand_listed_hash_is_blocked` |
| Dependency order enforced | `test_sanctions_before_identity_is_dependency_error`, `test_pep_before_sanctions_is_dependency_error` |
| Hallucination-drift failure | `test_drift_in_downstream_step_fails_chain`, `test_drift_in_identity_step_fails_chain` |
| Hash-chained audit, tamper-evident | `test_audit_tampered_entry_breaks_verification`, `test_audit_deleted_middle_entry_breaks_verification` |
| Email dry-run by default, refused in CI | `test_email_channel_defaults_to_dry_run`, `test_email_refused_in_ci` |

## Built / Written-not-run / Planned

| Item | Status |
|---|---|
| Dependency-aware 5-step chain | Built, 80 tests green |
| Fuzzy + transliteration-variant screening | Built |
| Re-grounding + drift check | Built |
| Hash-chained audit log | Built |
| Human-review escalation + confirmation gates | Built |
| View-aware SQLite authorizer, row cap, PII redaction, cost guard, brand guard | Built |
| Offline demo (4 synthetic customers) | Built |
| Real watchlist / identity-provider integration | Planned — deliberately absent; would need a licensed data source |
| Live email delivery | Planned — dry-run only today |
| Web UI / API service | Planned |
| Deployment, PyPI release | Not planned for this scaffold; no claim made |

## Docs

- `docs/purpose.md` — who this is for
- `docs/architecture.md` — diagram + module map
- `docs/how-it-works.md` — step-by-step walkthrough
- `docs/excerpts-and-output.md` — real code excerpts with real output
- `docs/running-offline.md` — run instructions
- `docs/guardrails.md` — controls in detail
- `docs/limitations.md` — known failures, kept visible as tests
- `docs/built-vs-planned.md` — honest status table
- `docs/implementation-guide.md` — for adopters
- `docs/interview-points.md` — talking points
- `docs/threat-model.md` — STRIDE-style analysis
- `docs/adr.md` — architecture decision records
- `docs/related-repos.md` — neighbours, not duplicates
- `knowledge/` — distilled notes + standalone Mermaid diagrams

## Limitations (headline)

- The matcher is edit-similarity plus a small variant table, not a
  production screening engine: it will miss names outside its variant
  table and can over-match short names. Both failure modes are visible
  in tests, not hidden.
- Risk bands are rule-based placeholders, not a calibrated model.
- The audit log is in-memory; persistence is a planned item, not a
  present feature.
- Full detail: `docs/limitations.md`.
