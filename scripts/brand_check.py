"""Brand check: repo docs must not contain a blocked business name.

Blocked names are stored as hashes (see src/kyc_aml/brand.py), so this
script hashes normalized 2- and 3-word windows from every doc and
compares digests. No blocked name appears in plain text anywhere in
this repo. Exit code 1 on a hit.
"""

import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from kyc_aml.brand import BLOCKLIST_HASHES  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    assert BLOCKLIST_HASHES, "brand blocklist is empty; refusing to check"
    hits = []
    doc_files = [ROOT / "README.md"]
    doc_files += sorted((ROOT / "docs").glob("*.md"))
    doc_files += sorted((ROOT / "knowledge").glob("*.md"))
    for path in doc_files:
        words = re.findall(r"[a-z]+", path.read_text(errors="ignore").lower())
        for n in (2, 3):
            for i in range(len(words) - n + 1):
                digest = hashlib.sha256(
                    " ".join(words[i:i + n]).encode()).hexdigest()
                if digest in BLOCKLIST_HASHES:
                    hits.append(f"{path.relative_to(ROOT)} window {i}")
    for hit in hits:
        print("BRAND HIT:", hit)
    print(f"brand hits: {len(hits)}; blocklist size: {len(BLOCKLIST_HASHES)}")
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
