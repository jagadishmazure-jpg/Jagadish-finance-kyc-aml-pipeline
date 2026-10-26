# Security policy

This is a portfolio demonstration, not a compliance product. It must
never be connected to real customers, real watchlists, or a production
bank system.

## What is enforced (and proven by tests)

- SQLite reads go through views only; the authorizer denies direct
  base-table reads, `sqlite_master`, all writes, PRAGMA, ATTACH and
  schema changes. See `tests/test_store_authorizer.py`.
- PII (card numbers, email addresses, SSNs, phone numbers) is redacted
  from logs and error messages. See `tests/test_redaction_audit_budget_notify_brand.py`.
- Human confirmation gates fail closed on bypass, rejection, absence,
  low confidence and self-contradicting consent. Approvals are
  named-person, single-use, scoped and expiring.
- Audit entries are hash-chained; tampering or deleting an entry breaks
  verification.
- Email notification defaults to dry run, is refused in CI, and this
  repo holds no credentials.

## Reporting a vulnerability

Do not open a public issue with exploit details. Use the repo owner's
private vulnerability reporting on GitHub, or contact the owner
directly. Expect an acknowledgement, not a fix SLA: this is a personal
portfolio project.

## Out of scope

- Real sanctions data, real PEP data, real identity verification.
- Any claim of regulatory compliance: nothing here is certified
  against any regulation, and the README says so plainly.
