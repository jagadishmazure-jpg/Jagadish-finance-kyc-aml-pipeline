"""8-word overlap check: repo docs vs. a source text file.

Usage: python3 scripts/overlap_check.py <source-text-file>

Normalizes both sides (lower-case, punctuation stripped) and reports
any 8-word window that appears in both. Target: 0 hits. Exit code 1
when any hit is found, so the check can gate a release.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def windows(text: str, n: int = 8):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: overlap_check.py <source-text-file>")
        return 2
    source = windows(Path(sys.argv[1]).read_text(errors="ignore"))
    hits = []
    doc_files = [ROOT / "README.md"]
    doc_files += sorted((ROOT / "docs").glob("*.md"))
    doc_files += sorted((ROOT / "knowledge").glob("*.md"))
    for path in doc_files:
        for window in sorted(windows(path.read_text(errors="ignore")) & source):
            hits.append(f"{path.relative_to(ROOT)}: {window}")
    for hit in hits:
        print("OVERLAP:", hit)
    print(f"overlap hits: {len(hits)} across {len(doc_files)} doc files")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
