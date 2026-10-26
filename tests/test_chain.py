import pytest

from kyc_aml.chain import (Chain, DependencyError, DriftError)
from kyc_aml.models import CustomerRecord

SANCTIONS = [{"name": "Alaric Voss"}]
PEP = [{"name": "Mohamed Alar"}]


def cust(name="Elena Marsh", country="low-risk-land", id_type="passport"):
    return CustomerRecord(customer_id="CUST-TEST", full_name=name,
                          date_of_birth="1988-04-12", country=country,
                          id_type=id_type, id_number="SYN-1")


def test_clean_customer_approves():
    decision = Chain(SANCTIONS, PEP).run(cust())
    assert decision.outcome == "approve"
    assert decision.risk_band == "low"
    assert decision.escalated is False


def test_exact_sanctions_match_escalates_not_auto_rejects():
    decision = Chain(SANCTIONS, PEP).run(cust(name="Alaric Voss"))
    assert decision.outcome == "human_review"
    assert decision.escalated is True
    assert "fuzzy hit" in decision.reason


def test_escalated_step_still_satisfies_later_dependencies():
    # Regression: an escalated sanctions step once raised
    # DependencyError in PEP, turning a fuzzy hit into a chain failure.
    chain = Chain(SANCTIONS, PEP)
    chain.run(cust(name="Alaric Voss"))
    assert "pep" in chain.steps
    assert "decision" in chain.steps


def test_second_customer_not_contaminated_by_first_escalation():
    chain = Chain(SANCTIONS, PEP)
    chain.run(cust(name="Alaric Voss"))
    decision = chain.run(cust())
    assert decision.outcome == "approve"


def test_pep_transliteration_variant_escalates():
    decision = Chain(SANCTIONS, PEP).run(cust(name="Mohammed Alar"))
    assert decision.outcome == "human_review"


def test_high_risk_country_raises_band():
    decision = Chain(SANCTIONS, PEP).run(cust(country="high-risk-land"))
    assert decision.risk_band == "high"


def test_sanctions_before_identity_is_dependency_error():
    chain = Chain(SANCTIONS, PEP)
    with pytest.raises(DependencyError):
        chain.run_step_out_of_order("sanctions", cust())


def test_pep_before_sanctions_is_dependency_error():
    chain = Chain(SANCTIONS, PEP)
    chain.run_step_out_of_order("identity", cust())
    with pytest.raises(DependencyError):
        chain.run_step_out_of_order("pep", cust())


def test_decision_first_is_dependency_error():
    chain = Chain(SANCTIONS, PEP)
    with pytest.raises(DependencyError):
        chain.run_step_out_of_order("decision", cust())


def test_risk_before_pep_is_dependency_error():
    chain = Chain(SANCTIONS, PEP)
    chain.run_step_out_of_order("identity", cust())
    chain.run_step_out_of_order("sanctions", cust())
    with pytest.raises(DependencyError):
        chain.run_step_out_of_order("risk", cust())


def test_drift_in_downstream_step_fails_chain():
    chain = Chain(SANCTIONS, PEP)
    decision = chain.run(cust(),
                         tamper={"sanctions": {"full_name": "Someone Else"}})
    assert decision.outcome == "human_review"
    kinds = [e["kind"] for e in chain.audit.entries]
    assert "chain_failed" in kinds


def test_drift_in_identity_step_fails_chain():
    chain = Chain(SANCTIONS, PEP)
    decision = chain.run(cust(),
                         tamper={"identity": {"country": "elsewhere-land"}})
    assert decision.outcome == "human_review"


def test_chain_failure_notifies_review_queue():
    chain = Chain(SANCTIONS, PEP)
    chain.run(cust(), tamper={"pep": {"full_name": "Someone Else"}})
    assert len(chain.notify.sent) == 1


def test_escalated_case_audit_chain_verifies():
    chain = Chain(SANCTIONS, PEP)
    chain.run(cust(name="Alaric Voss"))
    assert chain.audit.verify() is True


def test_step_order_is_documented_sequence():
    from kyc_aml.chain import ORDER
    assert ORDER == ["identity", "sanctions", "pep", "risk", "decision"]


def test_each_step_re_grounds_from_source_record():
    chain = Chain(SANCTIONS, PEP)
    chain.run(cust())
    for result in chain.steps.values():
        assert result.grounded_facts["full_name"] == "Elena Marsh"
        assert result.grounded_facts["customer_id"] == "CUST-TEST"


def test_missing_id_type_fails_chain_to_review():
    decision = Chain(SANCTIONS, PEP).run(cust(id_type=""))
    assert decision.outcome == "human_review"
