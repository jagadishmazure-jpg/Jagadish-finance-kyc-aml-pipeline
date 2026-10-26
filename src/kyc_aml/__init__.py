"""KYC/AML due-diligence pipeline for the fictional Tarnmoor Bank.

All data handled here is SYNTHETIC. Nothing in this package talks to a
real sanctions list, a real regulator, or a real customer database.
Standard library only.
"""

from .models import Approval, CustomerRecord, Decision, ScreeningHit, StepResult

__all__ = ["Approval", "CustomerRecord", "Decision", "ScreeningHit", "StepResult"]
__version__ = "0.1.0"
