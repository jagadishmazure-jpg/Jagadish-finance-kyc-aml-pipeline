from kyc_aml.demo import run_demo


def test_demo_outcomes_for_synthetic_customers(capsys):
    results = run_demo()
    by_id = {r["customer_id"]: r for r in results}
    assert by_id["CUST-001"]["outcome"] == "approve"
    assert by_id["CUST-002"]["outcome"] == "human_review"
    assert by_id["CUST-003"]["outcome"] == "human_review"
    assert by_id["CUST-004"]["risk_band"] == "high"
    out = capsys.readouterr().out
    assert "SYNTHETIC" in out
    assert "chain valid: True" in out
