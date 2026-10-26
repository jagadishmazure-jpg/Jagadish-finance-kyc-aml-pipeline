# Related repos (cross-links, not duplication)

This repo covers one slice — customer due diligence and screening
with an auditable chain. Neighbouring portfolio work covers the
adjacent slices; link to those repos rather than re-implementing
them here:

- **Fraud detection agents** — transaction monitoring and alert
  triage; this repo does not do transaction scoring.
- **Compliance RAG** — grounding regulatory answers in source
  documents; this repo screens names, it does not interpret rules.
- **Credit memo / underwriting** — borrower risk and memo writing;
  this repo's risk band is an onboarding signal, not a credit
  decision.
- **PII guard** — general-purpose PII detection and redaction
  patterns; this repo applies a focused redactor to its own logs.
- **Document intelligence** — extraction from documents; this repo
  assumes structured synthetic records as input.

If a future repo overlaps this one (for example, a full onboarding
service), it should reuse the chain and gate contracts from here
and link back, rather than copying the matcher or the audit code.
