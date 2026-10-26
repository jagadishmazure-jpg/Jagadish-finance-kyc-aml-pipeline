import os

import pytest

from kyc_aml import brand
from kyc_aml.audit import AuditLog
from kyc_aml.budget import CostTracker, validate_cost
from kyc_aml.notify import EmailChannel
from kyc_aml.redaction import redact_record, redact_text, safe_error

CARD = "4111 1111 1111 1111"
CARD_DASHED = "4111-1111-1111-1111"
EMAIL = "someone@example.test"


def test_card_number_redacted():
    out = redact_text(f"card {CARD} on file")
    assert CARD not in out
    assert "4111" not in out
    assert "[CARD-REDACTED]" in out


def test_dashed_card_number_redacted():
    assert CARD_DASHED not in redact_text(CARD_DASHED)


def test_email_address_redacted():
    out = redact_text(f"contact {EMAIL}")
    assert EMAIL not in out
    assert "[EMAIL-REDACTED]" in out


def test_ssn_redacted():
    out = redact_text("ssn 123-45-6789")
    assert "123-45-6789" not in out
    assert "[SSN-REDACTED]" in out


def test_phone_redacted():
    out = redact_text("call +1 555 123 4567")
    assert "555 123 4567" not in out
    assert "[PHONE-REDACTED]" in out


def test_safe_error_never_carries_card_or_email():
    err = safe_error(f"failed for {EMAIL} card {CARD}")
    assert EMAIL not in str(err)
    assert "4111" not in str(err)


def test_audit_payload_redacts_pii():
    log = AuditLog()
    entry = log.append("step:sanctions", {"note": f"card {CARD}",
                                          "email": EMAIL})
    assert CARD not in str(entry)
    assert EMAIL not in str(entry)


def test_audit_chain_verifies():
    log = AuditLog()
    log.append("step:identity", {"customer_id": "C1"})
    log.append("step:sanctions", {"customer_id": "C1"})
    assert log.verify() is True


def test_audit_tampered_entry_breaks_verification():
    log = AuditLog()
    log.append("step:identity", {"customer_id": "C1"})
    log.append("step:sanctions", {"customer_id": "C1"})
    log.entries[0]["payload"]["customer_id"] = "C2"
    assert log.verify() is False


def test_audit_deleted_middle_entry_breaks_verification():
    log = AuditLog()
    for kind in ("a", "b", "c"):
        log.append(kind, {"x": kind})
    del log.entries[1]
    assert log.verify() is False


def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        validate_cost(-0.01)


def test_negative_cost_add_rejected_and_spent_unchanged():
    tracker = CostTracker(100.0)
    with pytest.raises(ValueError):
        tracker.add(-5.0)
    assert tracker.spent == 0.0


def test_negative_budget_rejected():
    with pytest.raises(ValueError):
        CostTracker(-1.0)


def test_zero_cost_allowed():
    assert validate_cost(0) == 0.0


def test_over_budget_flag():
    tracker = CostTracker(10.0)
    tracker.add(11.0)
    assert tracker.over_budget() is True


def test_email_channel_defaults_to_dry_run():
    assert EmailChannel().dry_run is True


def test_email_dry_run_records_redacted_notice():
    channel = EmailChannel()
    record = channel.notify_review("C1", f"hit for {EMAIL}")
    assert EMAIL not in record["body"]
    assert len(channel.sent) == 1


def test_email_refused_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")
    with pytest.raises(RuntimeError):
        EmailChannel().notify_review("C1", "review")


def test_email_live_send_not_implemented():
    monkeypatch_env = os.environ.pop("CI", None)
    try:
        with pytest.raises(RuntimeError):
            EmailChannel(dry_run=False).notify_review("C1", "review")
    finally:
        if monkeypatch_env is not None:
            os.environ["CI"] = monkeypatch_env


def test_brand_blocklist_is_non_empty():
    assert len(brand.BLOCKLIST_HASHES) > 0


def test_brand_tarnmoor_not_blocked():
    assert brand.check_brand_ok("Tarnmoor Bank") is True


def test_brand_listed_hash_is_blocked():
    digest = next(iter(brand.BLOCKLIST_HASHES))
    assert brand.is_blocked_hash(digest) is True


def test_brand_empty_blocklist_refuses_check(monkeypatch):
    monkeypatch.setattr(brand, "BLOCKLIST_HASHES", frozenset())
    with pytest.raises(ValueError):
        brand.check_brand_ok("Tarnmoor Bank")
