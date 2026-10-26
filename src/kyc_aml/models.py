"""Plain data types for the pipeline. No I/O, no network, no secrets."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CustomerRecord:
    """A SYNTHETIC customer record. Invented people only."""

    customer_id: str
    full_name: str
    date_of_birth: str  # ISO date, synthetic
    country: str
    id_type: str
    id_number: str  # synthetic identifier, never a real person's document
    email: str = ""
    card_number: str = ""  # synthetic, used only to prove redaction


@dataclass
class ScreeningHit:
    list_name: str  # e.g. "synthetic-sanctions" or "synthetic-pep"
    matched_name: str
    score: float  # 0.0 - 1.0 fuzzy similarity
    variants_used: list = field(default_factory=list)


@dataclass
class StepResult:
    step: str
    status: str  # "passed" | "failed" | "escalated"
    grounded_facts: dict = field(default_factory=dict)
    hits: list = field(default_factory=list)
    detail: str = ""
    created_at: str = field(default_factory=utcnow_iso)


@dataclass
class Decision:
    outcome: str  # "approve" | "reject" | "human_review"
    risk_band: str  # "low" | "medium" | "high"
    reason: str
    escalated: bool = False


@dataclass
class Approval:
    """A named-person, single-use, scoped, expiring approval.

    An approval is consumed the first time it is used. Reuse, a wrong
    scope, a missing approver name, or an expired approval all fail.
    """

    approver: str
    scope: str
    expires_at: str  # ISO timestamp
    used: bool = False

    def is_valid(self, scope: str, now_iso: str) -> bool:
        if self.used:
            return False
        if not self.approver or not self.approver.strip():
            return False
        if self.scope != scope:
            return False
        return now_iso <= self.expires_at

    def consume(self, scope: str, now_iso: str) -> None:
        if not self.is_valid(scope, now_iso):
            raise ValueError("approval is not valid for this scope at this time")
        self.used = True
