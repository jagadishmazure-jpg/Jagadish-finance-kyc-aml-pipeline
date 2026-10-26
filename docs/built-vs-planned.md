# Built vs planned

| Item | Status | Evidence |
|---|---|---|
| 5-step dependency-aware chain | Built | `tests/test_chain.py` |
| Fuzzy + variant screening | Built | `tests/test_matching.py` |
| Re-grounding + drift failure | Built | drift tests in `test_chain.py` |
| Hash-chained audit | Built | audit tests |
| Human-review escalation + gates | Built | `tests/test_gates.py` |
| View-aware authorizer | Built | `tests/test_store_authorizer.py` |
| Row cap, cost guard, PII redaction, brand guard | Built | redaction/budget/brand tests |
| Dry-run review notices | Built | notify tests |
| Offline demo (4 synthetic customers) | Built | `tests/test_demo.py` |
| Persistent audit storage | Planned | — |
| Real watchlist / identity providers | Planned | needs licensed data |
| Live email delivery | Planned | dry-run only today |
| Web UI / API | Planned | — |
| Deployment, PyPI, CI badges | Not planned | no claim made anywhere |

Test count at last full run: 80 passed (system python3/pytest).
