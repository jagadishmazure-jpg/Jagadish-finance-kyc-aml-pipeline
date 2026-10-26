# Real code excerpts and their real output

## Drift check (from `src/kyc_aml/chain.py`)

```python
def _check_drift(step, facts, verified):
    for key, value in facts.items():
        if key in verified and verified[key] != value:
            raise DriftError(
                f"drift in step {step}: field {key} contradicts verified fact")
```

## Authorizer rule (from `src/kyc_aml/store.py`)

```python
if param1 in BASE_TABLES:
    return (sqlite3.SQLITE_OK if source in ALLOWED_VIEWS
            else sqlite3.SQLITE_DENY)
```

Verified live in a scratch check: a direct base-table read arrives
with no source and is denied; the same read through a view arrives
with the view name as source and is allowed.

## Demo output (real run, 4 synthetic customers)

```text
Tarnmoor Bank (fictional) -- KYC/AML demo, SYNTHETIC data only
CUST-001: approve (low) -- all steps passed, no hits
CUST-002: human_review (medium) -- fuzzy hit requires human review
CUST-003: human_review (medium) -- fuzzy hit requires human review
CUST-004: approve (high) -- all steps passed, no hits
audit entries: 24, chain valid: True
```

## Screening output (real run)

```python
>>> screen_name("Mohammed Alar", [{"name": "Mohamed Alar"}], "synthetic-pep")
[{'list_name': 'synthetic-pep', 'matched_name': 'Mohamed Alar',
  'score': 0.96, 'variants_used': ['mohammed alar']}]
```

## Test suite (real run)

```text
80 passed in 0.13s
```

Sample sizes, stated plainly: the demo covers 4 synthetic customers;
the suite is 80 regression checks written for this repo. Neither is
a measurement of screening accuracy on real data, and neither is
presented as one.
