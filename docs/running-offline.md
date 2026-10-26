# How to run (offline first)

Requirements: Python 3.12 (system python3 is fine) and pytest.
No other packages, no install step, no virtual environment inside
this repo.

```bash
python3 -m pytest tests/ -q
PYTHONPATH=src python3 -m kyc_aml.demo
python3 scripts/brand_check.py
```

Optional checks (need the source text file, which is intentionally
NOT committed to this repo — see the overlap note below):

```bash
python3 scripts/overlap_check.py /path/to/source-text.txt
```

## Overlap note

The distilled notes in `knowledge/` were written in the author's own
words from a finance AI program brochure. The brochure itself is not
committed, no sentence is copied from it, and no affiliation with its
publisher is claimed. The overlap script checks every 8-word window
in the README, `docs/` and `knowledge/` against the extracted source
text; the required result is 0 hits.
