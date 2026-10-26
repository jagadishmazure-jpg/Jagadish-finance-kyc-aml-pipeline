# Implementation guide (for adopters)

## Use the chain, not the demo

```python
from kyc_aml.chain import Chain
from kyc_aml.models import CustomerRecord

chain = Chain(sanctions_list, pep_list)  # your own lists, same shape
decision = chain.run(CustomerRecord(...))
assert chain.audit.verify()
```

- One `Chain` per batch is fine: `run()` resets per-customer state
  while the audit log accumulates. Do not share a `CustomerRecord`
  across runs without re-reading it from source.
- Treat `human_review` as the normal outcome for any hit. Build your
  reviewer UI around the audit entries, not around the decision
  string alone.

## Use the store constructors

Always obtain connections via `create_store()` or
`create_seeded_store()`. A raw `sqlite3.connect` bypasses the
authorizer entirely — that is a property of SQLite authorizers, and
this repo documents it rather than pretending otherwise. Read only
through the `v_*` views, and keep `MAX_ROWS` small.

## Wire the gate into your review flow

```python
from kyc_aml.gates import ConfirmationGate
gate = ConfirmationGate("release-escalated-case")
gate.confirm(reviewer_text, approval, now_iso)  # raises GateDenied otherwise
```

Issue approvals from your own identity system, with a named person,
a scope string that matches the gate, a short expiry, and
single-use semantics. Never pre-approve a batch.

## Replace, don't extend, the demo pieces

- The matcher: swap in a licensed screening engine; keep the
  escalate-on-hit contract.
- The risk rules: swap in a calibrated model; keep the rule that the
  band derives from grounded facts, not from prior prose.
- The notify channel: swap in a real sender behind the same
  dry-run-by-default flag and CI refusal.
- The audit log: persist entries append-only and verify the chain on
  read, not just on write.
