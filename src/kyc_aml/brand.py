"""Brand / name collision guard.

The blocklist is stored as SHA-256 hashes only, never as plain names,
so this file cannot itself leak a real business name into the repo.
``is_blocked_name`` hashes its input the same way and compares hashes.
The list must stay non-empty -- a test asserts that -- because an
empty blocklist checks nothing.
"""

from __future__ import annotations

import hashlib

# SHA-256 hex digests of names this fictional brand must not collide
# with. Deliberately opaque: do not "decode" them back into names here.
BLOCKLIST_HASHES = frozenset({
    "309e31536dcf1556bb6c81b00cd992445b79ad8e89f9c0cd2a1f0675342538b3",
    "2cbb9e58bf3bcbdfe805a2aebb57f84531b114a18e5f0e6377d9f5a7bf86576b",
    "4b1f6f530975ef68d8f30d663efe02fb1e20ca2fdde8c5416ecfeb21fb881e96",
    "311ff2d71234e230eb559f843c1f5c548302246a365221713da47017e656e672",
    "ce749e840dcada0f9196edd49327ae5b3ab16f1d0405e72c1cb7d62b04538a42",
    "71f566aba763fb7636f03bfeb321c6d4934d4a6d5cb777c49b1c1595260c573b",
    "7105a46cb4c2810f0c916e0bb4b4e4ef834ad42040c471b42c96d356a9fd1b21",
    "6228a5824a1e8d1554519125795ad14c1b7be681c6e9efbbbc66c91bbf2f89e5",
})


def _digest(name: str) -> str:
    return hashlib.sha256(name.strip().lower().encode()).hexdigest()


def is_blocked_hash(digest: str) -> bool:
    return digest in BLOCKLIST_HASHES


def is_blocked_name(name: str) -> bool:
    return _digest(name) in BLOCKLIST_HASHES


def check_brand_ok(name: str) -> bool:
    """True when a proposed fictional brand name is not blocked."""
    if not BLOCKLIST_HASHES:
        raise ValueError("brand blocklist is empty; refusing to check")
    return not is_blocked_name(name)
