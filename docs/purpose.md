# Purpose

## Who this is for

- Engineers learning how regulated onboarding pipelines are put
  together: ordered checks, screening, scoring, decision, audit.
- Reviewers who want to see guardrails proven by tests rather than
  asserted in prose: every enforcement claim in the README names its
  test.
- Adopters sketching their own due-diligence workflow who need a
  small, readable reference instead of a framework.

## What it is not

- Not a screening product: the lists are invented, the matcher is
  deliberately simple, and no result here should be used to judge a
  real person.
- Not legal or compliance advice, and not evidence of meeting any
  rulebook. A real deployment would need licensed data, legal review,
  and regulator-grade record retention — all out of scope here.

## Design idea in one paragraph

Treat the pipeline as a chain of evidence, not a chain of text. Each
step starts again from the source record, so a mistake in one step
cannot become the input of the next. When a later step disagrees with
an earlier verified fact, the chain stops and a human takes over,
instead of the disagreement being averaged away. Everything that
happened is written to a log whose entries are chained by hash, so a
later edit is detectable.
