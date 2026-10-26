"""Hash-chained audit log.

Every step, input summary and decision appends one entry. Each entry's
hash covers the previous entry's hash, so deleting or editing a middle
entry breaks verification of everything after it. Payloads stored here
are already redacted by the caller (see redaction.py); the log never
stores raw customer PII.
"""

from __future__ import annotations

import hashlib
import json

GENESIS = "0" * 64


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def entry_hash(prev_hash: str, payload: dict) -> str:
    return hashlib.sha256((prev_hash + _canonical(payload)).encode()).hexdigest()


class AuditLog:
    def __init__(self) -> None:
        self.entries: list = []
        self._prev = GENESIS

    def append(self, kind: str, payload: dict) -> dict:
        from .redaction import redact_record

        clean = redact_record(payload)
        entry = {
            "seq": len(self.entries) + 1,
            "kind": kind,
            "payload": clean,
            "prev_hash": self._prev,
        }
        entry["entry_hash"] = entry_hash(self._prev, clean)
        self._prev = entry["entry_hash"]
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        prev = GENESIS
        for entry in self.entries:
            if entry["prev_hash"] != prev:
                return False
            if entry["entry_hash"] != entry_hash(prev, entry["payload"]):
                return False
            prev = entry["entry_hash"]
        return True
