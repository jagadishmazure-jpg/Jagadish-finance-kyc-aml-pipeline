"""Screening cost tracking. Costs are plain numbers, never negative.

A negative cost estimate is a data error (it would let a budget cap be
bypassed, as a negative charge once did in another repo). It is rejected
at the boundary, not clamped to zero.
"""

from __future__ import annotations


def validate_cost(amount) -> float:
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("cost must be a number")
    if amount < 0:
        raise ValueError("cost must not be negative")
    return float(amount)


class CostTracker:
    def __init__(self, budget: float) -> None:
        self.budget = validate_cost(budget)
        self.spent = 0.0

    def add(self, amount) -> float:
        amount = validate_cost(amount)
        self.spent += amount
        return self.spent

    def over_budget(self) -> bool:
        return self.spent > self.budget
