"""Human-confirmation gates.

A gate passes ONLY on a clean, unambiguous affirmation from a named
approver holding a valid approval. Everything else fails closed:

- bypass: no approval object at all -> GateDenied
- reject: an explicit "no" -> GateDenied
- absent: no response text at all -> GateDenied
- low confidence: hedges ("maybe", "i guess", "probably", "unsure",
  a trailing "?") -> GateDenied
- self-contradicting consent: text containing both an affirmation and
  a refusal ("yes, wait, no") -> GateDenied

Tests assert on the exception type and the gate outcome, never on
SQLite-style error message text (see the authorizer tests for the same
rule applied to database errors).
"""

from __future__ import annotations

import re

from .models import Approval

AFFIRMATIONS = {"yes", "approve", "approved", "confirm", "confirmed", "go ahead"}
REFUSALS = {"no", "reject", "rejected", "deny", "denied", "stop", "cancel"}
HEDGES = {"maybe", "guess", "probably", "perhaps", "unsure", "not sure",
          "wait", "hold on", "hmm"}


class GateDenied(ValueError):
    pass


def _tokens(text: str) -> list:
    return re.findall(r"[a-z]+", text.lower())


def classify_consent(text) -> str:
    """Return 'approve' | 'reject' | 'absent' | 'low_confidence' |
    'contradicting'. Only 'approve' may open a gate."""
    if text is None or not str(text).strip():
        return "absent"
    tokens = set(_tokens(str(text)))
    has_yes = bool(tokens & AFFIRMATIONS)
    has_no = bool(tokens & REFUSALS)
    if has_yes and has_no:
        return "contradicting"
    if has_no:
        return "reject"
    if not has_yes:
        return "reject"
    if tokens & HEDGES or str(text).strip().endswith("?"):
        return "low_confidence"
    return "approve"


class ConfirmationGate:
    def __init__(self, scope: str) -> None:
        self.scope = scope

    def confirm(self, consent_text, approval: Approval, now_iso: str) -> bool:
        if approval is None:
            raise GateDenied("confirmation requires an approval")
        if classify_consent(consent_text) != "approve":
            raise GateDenied("consent was not a clean affirmation")
        if not approval.is_valid(self.scope, now_iso):
            raise GateDenied("approval is missing, used, expired or out of scope")
        approval.consume(self.scope, now_iso)
        return True
