"""Fuzzy name matching with transliteration variants.

The lists screened here are SYNTHETIC, invented for this repo. Matching
is deliberately conservative: a near miss is an escalation to a human,
never an automatic rejection on its own.
"""

from __future__ import annotations

import difflib
import re
import unicodedata

# Common spelling variants for a small set of given names. Keys and
# values are generic name spellings, not entries from any real list.
NAME_VARIANTS = {
    "mohamed": {"mohamed", "mohammed", "muhammad", "mohammad", "mehmed"},
    "yousef": {"yousef", "yusuf", "youssef", "joseph"},
    "ahmed": {"ahmed", "ahmad", "achmed"},
    "katarina": {"katarina", "katherine", "catherine", "katrina"},
    "alexander": {"alexander", "alexandre", "aleksandr"},
    "ivan": {"ivan", "john", "jan"},
}


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_name(name: str) -> str:
    """Lower-case, de-accent, drop punctuation, collapse whitespace."""
    text = strip_diacritics(name).lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def name_variants(name: str) -> set:
    """All spelling variants of a normalized name, token by token."""
    tokens = normalize_name(name).split()
    variants = {normalize_name(name)}
    for i, token in enumerate(tokens):
        for alt in NAME_VARIANTS.get(token, {token}):
            new_tokens = tokens[:]
            new_tokens[i] = alt
            variants.add(" ".join(new_tokens))
    return variants


def similarity(a: str, b: str) -> float:
    """Best difflib ratio across the transliteration variants of ``a``."""
    best = 0.0
    for variant in name_variants(a):
        score = difflib.SequenceMatcher(None, variant, normalize_name(b)).ratio()
        best = max(best, score)
    return best


def screen_name(name: str, watchlist: list, list_name: str,
                threshold: float = 0.70) -> list:
    """Return hits at or above ``threshold``, best first.

    Scores below the threshold are not hits at all; scores at or above
    it are returned so the caller can escalate them to a human.
    """
    hits = []
    for entry in watchlist:
        entry_name = entry["name"] if isinstance(entry, dict) else str(entry)
        score = similarity(name, entry_name)
        if score >= threshold:
            hits.append({
                "list_name": list_name,
                "matched_name": entry_name,
                "score": round(score, 4),
                "variants_used": sorted(name_variants(name)),
            })
    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits
