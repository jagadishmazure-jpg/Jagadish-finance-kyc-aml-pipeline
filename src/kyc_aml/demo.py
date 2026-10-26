"""Offline demo: three synthetic customers through the chain."""

from __future__ import annotations

import json
import os

from .chain import Chain
from .models import CustomerRecord

HERE = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


def load_synthetic():
    base = os.path.join(HERE, "data")
    with open(os.path.join(base, "synthetic_customers.json")) as fh:
        customers = json.load(fh)
    with open(os.path.join(base, "synthetic_sanctions.json")) as fh:
        lists = json.load(fh)
    return customers, lists


def run_demo() -> list:
    customers, lists = load_synthetic()
    chain = Chain(lists["sanctions"], lists["pep"])
    results = []
    for raw in customers:
        record = CustomerRecord(**raw)
        # One chain object holds the shared audit log; run() resets
        # per-customer step state, so customers cannot leak into each
        # other (regression: an earlier escalated customer once forced
        # every later customer into human_review).
        decision = chain.run(record)
        results.append({
            "customer_id": record.customer_id,
            "outcome": decision.outcome,
            "risk_band": decision.risk_band,
            "reason": decision.reason,
        })
    print("Tarnmoor Bank (fictional) -- KYC/AML demo, SYNTHETIC data only")
    for row in results:
        print(f"{row['customer_id']}: {row['outcome']} "
              f"({row['risk_band']}) -- {row['reason']}")
    print(f"audit entries: {len(chain.audit.entries)}, "
          f"chain valid: {chain.audit.verify()}")
    return results


if __name__ == "__main__":
    run_demo()
