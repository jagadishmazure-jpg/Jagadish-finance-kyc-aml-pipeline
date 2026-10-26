"""Dependency-aware KYC/AML chain with re-grounding and drift checks.

Order is fixed and enforced: identity -> sanctions -> PEP -> risk ->
decision. A step refuses to run unless every dependency has passed;
the chain records that refusal as a failure, never silently skips.

Compounding-error guard: every step re-reads its inputs from the
original source record (``grounded_facts``) instead of trusting the
previous step's output. After each step, the drift check compares the
step's facts against the verified upstream facts; any contradiction
fails the whole chain and escalates it to a human reviewer.

Escalation: a fuzzy hit at or above the review threshold, or any chain
failure, produces a ``human_review`` outcome and a dry-run review
notice. Nothing auto-rejects on a fuzzy hit alone.
"""

from __future__ import annotations

from .audit import AuditLog
from .gates import ConfirmationGate
from .matching import screen_name
from .models import CustomerRecord, Decision, StepResult
from .notify import EmailChannel

ORDER = ["identity", "sanctions", "pep", "risk", "decision"]
DEPENDENCIES = {
    "identity": [],
    "sanctions": ["identity"],
    "pep": ["identity", "sanctions"],
    "risk": ["identity", "sanctions", "pep"],
    "decision": ["identity", "sanctions", "pep", "risk"],
}
REVIEW_THRESHOLD = 0.75
HIGH_RISK_COUNTRIES = frozenset({"high-risk-land", "sanctioned-region"})


class DependencyError(ValueError):
    pass


class DriftError(ValueError):
    pass


def grounded_facts(customer: CustomerRecord) -> dict:
    """The verified facts, copied fresh from the source record."""
    return {
        "customer_id": customer.customer_id,
        "full_name": customer.full_name,
        "date_of_birth": customer.date_of_birth,
        "country": customer.country,
        "id_type": customer.id_type,
    }


def _check_drift(step: str, facts: dict, verified: dict) -> None:
    for key, value in facts.items():
        if key in verified and verified[key] != value:
            raise DriftError(
                f"drift in step {step}: field {key} contradicts verified fact")


class Chain:
    def __init__(self, sanctions_list, pep_list,
                 review_threshold: float = REVIEW_THRESHOLD,
                 notify: EmailChannel | None = None) -> None:
        self.sanctions_list = sanctions_list
        self.pep_list = pep_list
        self.review_threshold = review_threshold
        self.notify = notify or EmailChannel(dry_run=True)
        self.audit = AuditLog()
        self.steps: dict = {}
        self.escalated = False

    def _run_step(self, step: str, customer: CustomerRecord,
                  tamper: dict | None = None) -> StepResult:
        for dep in DEPENDENCIES[step]:
            prior = self.steps.get(dep)
            # "escalated" still satisfies a dependency: the step ran and
            # produced a result, it just needs a human. Only a missing
            # or failed step blocks the chain. Without this, a sanctions
            # hit would abort the chain instead of escalating it.
            if prior is None or prior.status not in ("passed", "escalated"):
                raise DependencyError(
                    f"step {step} cannot run: dependency {dep} has not passed")
        facts = grounded_facts(customer)
        if tamper and step in tamper:
            facts.update(tamper[step])
        _check_drift(step, facts, grounded_facts(customer))
        hits = []
        if step == "sanctions":
            hits = screen_name(customer.full_name, self.sanctions_list,
                               "synthetic-sanctions",
                               threshold=self.review_threshold)
        if step == "pep":
            hits = screen_name(customer.full_name, self.pep_list,
                               "synthetic-pep",
                               threshold=self.review_threshold)
        result = StepResult(step=step, status="passed",
                            grounded_facts=facts,
                            hits=[type("H", (), h) for h in hits])
        if step in ("sanctions", "pep") and hits:
            result.status = "escalated"
            self.escalated = True
        self.steps[step] = result
        self.audit.append(f"step:{step}", {
            "step": step, "status": result.status,
            "customer_id": customer.customer_id,
            "hit_count": len(hits),
        })
        return result

    def run(self, customer: CustomerRecord,
            tamper: dict | None = None) -> Decision:
        """Run the full chain. Returns a Decision; failures escalate."""
        # Per-customer state resets each run; the audit log persists
        # across customers so one log covers the whole batch.
        self.steps = {}
        self.escalated = False
        try:
            identity = self._run_step("identity", customer, tamper)
            if not identity.grounded_facts["id_type"]:
                raise ValueError("identity verification failed: no id type")
            self._run_step("sanctions", customer, tamper)
            self._run_step("pep", customer, tamper)
            risk = self._run_step("risk", customer, tamper)
            # Risk band is derived from grounded facts only.
            band = "low"
            if customer.country in HIGH_RISK_COUNTRIES:
                band = "high"
            elif self.escalated:
                band = "medium"
            risk.grounded_facts["risk_band"] = band
            self._run_step("decision", customer, tamper)
        except (DependencyError, DriftError, ValueError) as exc:
            self.escalated = True
            self.audit.append("chain_failed", {
                "customer_id": customer.customer_id,
                "error_type": type(exc).__name__,
            })
            self.notify.notify_review(customer.customer_id, "chain failure")
            return Decision(outcome="human_review", risk_band="high",
                            reason=f"chain failed: {type(exc).__name__}",
                            escalated=True)
        if self.escalated:
            self.audit.append("decision", {
                "customer_id": customer.customer_id, "outcome": "human_review"})
            self.notify.notify_review(customer.customer_id,
                                      "fuzzy screening hit at review threshold")
            return Decision(outcome="human_review", risk_band=band,
                            reason="fuzzy hit requires human review",
                            escalated=True)
        self.audit.append("decision", {
            "customer_id": customer.customer_id, "outcome": "approve"})
        return Decision(outcome="approve", risk_band=band,
                        reason="all steps passed, no hits", escalated=False)

    def run_step_out_of_order(self, step: str,
                              customer: CustomerRecord) -> StepResult:
        """Public helper used by tests to prove ordering is enforced."""
        return self._run_step(step, customer)


def approve_escalated_case(gate: ConfirmationGate, consent_text,
                           approval, now_iso: str) -> bool:
    """A human reviewer releases an escalated case through the gate."""
    return gate.confirm(consent_text, approval, now_iso)
