import pytest

from kyc_aml.gates import ConfirmationGate, GateDenied, classify_consent
from kyc_aml.models import Approval

NOW = "2026-10-26T12:00:00+00:00"
LATER = "2026-10-27T12:00:00+00:00"


def approval(**over):
    base = dict(approver="Priya Nair", scope="release-escalated-case",
                expires_at="2026-10-27T00:00:00+00:00")
    base.update(over)
    return Approval(**base)


def test_clean_yes_passes_gate():
    gate = ConfirmationGate("release-escalated-case")
    assert gate.confirm("yes", approval(), NOW) is True


def test_gate_bypass_without_approval_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("yes", None, NOW)


def test_gate_reject_on_explicit_no():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("no", approval(), NOW)


def test_gate_absent_empty_response_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("", approval(), NOW)


def test_gate_absent_none_response_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm(None, approval(), NOW)


def test_gate_low_confidence_maybe_yes_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("maybe yes", approval(), NOW)


def test_gate_low_confidence_i_guess_yes_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("i guess yes", approval(), NOW)


def test_gate_low_confidence_question_yes_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("yes?", approval(), NOW)


def test_gate_contradicting_yes_wait_no_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("yes, wait, no", approval(), NOW)


def test_gate_contradicting_yes_then_no_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("yes but actually no", approval(), NOW)


def test_gate_approval_is_single_use():
    gate = ConfirmationGate("release-escalated-case")
    appr = approval()
    gate.confirm("yes", appr, NOW)
    with pytest.raises(GateDenied):
        gate.confirm("yes", appr, NOW)


def test_gate_expired_approval_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("yes", approval(), LATER)


def test_gate_wrong_scope_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("yes", approval(scope="other-scope"), NOW)


def test_gate_anonymous_approver_denied():
    gate = ConfirmationGate("release-escalated-case")
    with pytest.raises(GateDenied):
        gate.confirm("yes", approval(approver="  "), NOW)


def test_classify_consent_table():
    assert classify_consent("yes") == "approve"
    assert classify_consent("no") == "reject"
    assert classify_consent("") == "absent"
    assert classify_consent(None) == "absent"
    assert classify_consent("maybe yes") == "low_confidence"
    assert classify_consent("yes, wait, no") == "contradicting"
