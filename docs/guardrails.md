# Guardrails and security controls

## Data access

- The SQLite authorizer is the enforcement point, not a wrapper
  convention: SQLite itself denies the query. Base-table reads pass
  only when the read comes through an allowed view; `sqlite_master`
  reads, writes, PRAGMA, ATTACH, schema changes and extension loading
  are all denied.
- Views expose no PII columns (`full_name`, `email` are absent from
  `v_customers`); tests assert the column list.
- Row caps happen at fetch time with `fetchmany(MAX + 1)`. The code
  never rewrites a query with LIMIT and never calls `fetchall` on an
  unbounded result, so a caller cannot silently widen a query.

## PII

- Redaction covers card numbers, email addresses, SSNs and phone
  numbers. Audit payloads are redacted on append; error messages go
  through `safe_error`. Tests feed a real-looking card number and an
  email address through both paths and assert neither survives.

## Human control

- Fuzzy hits escalate; they never auto-reject. Chain failures
  escalate. Release requires a clean affirmation plus a valid
  approval. The gate's failure modes (bypass, reject, absent,
  low-confidence, contradicting) each have a test.
- Approvals carry a named approver, a scope, an expiry, and a
  single-use flag. Reuse, wrong scope, expiry and anonymous approvers
  are all denied by test.

## Money and messaging

- Cost inputs reject negatives at the boundary, so a negative charge
  cannot cancel out real spend against a budget cap.
- Email defaults to dry run, is refused when `CI` is set, and the
  module has no credentials and no network code. Live delivery is a
  planned item, not a hidden capability.

## Names

- The fictional brand is checked against a blocklist stored as
  hashes, never plain names. A test asserts the blocklist is
  non-empty, because an empty list would check nothing.
