# Distilled notes — due-diligence pipeline patterns

Written in the author's own words from study material on AI in
finance. No sentences are copied from the source, no affiliation is
claimed, and the source document itself is not stored in this repo.

## The core pattern

Onboarding work in a bank breaks into a sequence where each stage
depends on the one before it: confirm who the person is, check them
against restriction and prominent-person lists, form a risk view,
then decide. The sequence matters because a later stage is only
meaningful if the earlier stages actually ran and passed.

## Why chains drift

When several automated stages feed each other, a small mistake in an
early stage becomes the assumed truth of the next stage. By the end,
the result can look confident while resting on a wrong premise. Two
countermeasures show up repeatedly:

1. **Re-ground every stage.** Each stage should start from the
   original evidence (the record, the list entry), not from the
   previous stage's summary.
2. **Check for contradiction.** If a later stage's facts disagree
   with an earlier verified fact, stop and escalate instead of
   smoothing over the disagreement.

## Screening is a human decision aid, not a verdict

Name matching is inherently fuzzy: spelling varies across languages
and scripts, and different people share similar names. A sensible
design therefore treats a close match as a reason to look, not as a
reason to refuse. Thresholds decide how much human time is spent, and
they should be set with that trade-off in view, not tuned to make a
demo look decisive.

## Auditability is the product

In regulated work, the ability to reconstruct what happened matters
as much as the decision itself: which lists were checked, what
matched, who approved a release, and in what order. A log that can be
quietly edited afterwards is not evidence, which is why chaining log
entries by hash is worth the small implementation cost.

## What this repo takes from these notes

- Ordered stages with enforced dependencies (`chain.py`).
- Fuzzy matching with spelling variants (`matching.py`).
- Re-grounding plus a drift check that fails the chain (`chain.py`).
- Escalation to a human on any hit or failure (`chain.py`,
  `gates.py`, `notify.py`).
- A hash-chained, redacted audit log (`audit.py`, `redaction.py`).

## Diagrams

- `knowledge/architecture.mmd` — system overview
- `knowledge/chain-sequence.mmd` — the five stages in order
- `knowledge/screening.mmd` — how a name is matched
