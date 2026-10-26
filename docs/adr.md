# Architecture decision records

## ADR-1: Escalated steps satisfy dependencies

- **Context:** a sanctions hit marks its step "escalated", not
  "passed". Strictly requiring "passed" blocked the rest of the chain.
- **Decision:** "passed" or "escalated" both satisfy a dependency;
  only missing/failed steps block.
- **Consequence:** a fuzzy hit produces a completed chain ending in
  human review, with all downstream evidence collected.

## ADR-2: Enforcement in SQLite's authorizer, not in wrappers

- **Context:** read-through-views could be a coding convention.
- **Decision:** install a SQLite authorizer that denies everything
  except view-mediated reads.
- **Consequence:** the rule holds for any caller on the connection,
  but adopters must use the provided constructors.

## ADR-3: Redact at the boundary, not at display time

- **Context:** PII in logs is the most common leak in pipelines.
- **Decision:** audit append and error construction redact first;
  nothing downstream is trusted to redact.
- **Consequence:** raw records must never be passed to the log or
  to error constructors.

## ADR-4: No language model in this scaffold

- **Context:** chained model calls compound small errors.
- **Decision:** implement the chain structurally (deterministic
  matcher, re-grounding, drift check) with no model dependency.
- **Consequence:** the scaffold is fully offline and deterministic,
  and any future model step must pass the same drift check.

## ADR-5: Brand blocklist stored as hashes

- **Context:** a plain-text blocklist would itself publish the names
  it guards against.
- **Decision:** store SHA-256 digests; hash inputs the same way.
- **Consequence:** the list is opaque in the repo; tests assert
  non-emptiness and hash-membership rather than naming entries.
