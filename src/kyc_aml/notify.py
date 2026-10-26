"""Escalation notification channel.

Default is dry_run=True: nothing is ever sent unless the caller
explicitly opts in. Sending is REFUSED when the CI environment variable
is set, and this module holds no credentials and performs no network
I/O at all -- a real mail sender is a Planned item, not a hidden one.
In dry-run mode the rendered message is returned so tests can inspect
its (redacted) content.
"""

from __future__ import annotations

import os

from .redaction import redact_text


class EmailChannel:
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run
        self.sent: list = []  # dry-run outbox, for tests only

    def notify_review(self, case_id: str, reason: str) -> dict:
        message = redact_text(
            f"Human review requested for case {case_id}: {reason}")
        # Dry-run first: it transmits nothing, so it must never raise,
        # even when the runner sets CI. The CI refusal below only guards
        # the non-dry-run path, which is what it was meant to guard.
        if self.dry_run:
            record = {"to": "review-queue@fictional.invalid", "body": message}
            self.sent.append(record)
            return record
        if os.environ.get("CI"):
            raise RuntimeError("refusing to send email in CI")
        raise RuntimeError(
            "live sending is not implemented; use dry_run=True")
