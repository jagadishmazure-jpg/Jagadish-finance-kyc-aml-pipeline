"""SQLite store guarded by a strict view-aware authorizer.

Rule, enforced by SQLite itself (not by convention):
- A base-table read is allowed ONLY when the authorizer's source
  argument names an allowed view -- i.e. the read goes through a view.
  A direct ``SELECT ... FROM customers`` is denied by SQLite.
- ``sqlite_master`` / ``sqlite_sequence`` reads are denied.
- All writes, PRAGMA, ATTACH, DETACH, CREATE/DROP/ALTER and extension
  loading are denied once the authorizer is installed.
- Only the SELECT and READ authorizer actions are ever allowed.

Setup (table + view creation) happens BEFORE the authorizer is
installed, on the same connection; the returned connection is
read-through-views-only from then on.

Row caps: :func:`fetch_cases` uses ``fetchmany(MAX + 1)`` and raises
when the cap is exceeded. It never rewrites a query with LIMIT and
never calls fetchall on an unbounded result.
"""

from __future__ import annotations

import sqlite3

BASE_TABLES = {"customers", "cases", "audit_log"}
ALLOWED_VIEWS = {"v_customers", "v_cases", "v_audit"}
MAX_ROWS = 100

_SQLITE_READ = 20
_SQLITE_SELECT = 21


class RowCapExceeded(ValueError):
    pass


def _authorizer(action, param1, param2, db_name, source):
    if action == _SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == _SQLITE_READ:
        if param1 in ("sqlite_master", "sqlite_sequence"):
            return sqlite3.SQLITE_DENY
        if param1 in BASE_TABLES:
            # Direct base-table read: source is None. Via a view, SQLite
            # passes the view name as `source`. Only the latter passes.
            return (sqlite3.SQLITE_OK if source in ALLOWED_VIEWS
                    else sqlite3.SQLITE_DENY)
        if param1 in ALLOWED_VIEWS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_DENY


def create_store() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE TABLE customers (customer_id TEXT PRIMARY KEY, "
        "full_name TEXT, country TEXT, risk_band TEXT)")
    con.execute(
        "CREATE TABLE cases (case_id TEXT PRIMARY KEY, customer_id TEXT, "
        "outcome TEXT, risk_band TEXT)")
    con.execute(
        "CREATE TABLE audit_log (seq INTEGER PRIMARY KEY, entry_hash TEXT, "
        "prev_hash TEXT, payload TEXT)")
    con.execute(
        "CREATE VIEW v_customers AS SELECT customer_id, country, risk_band "
        "FROM customers")
    con.execute(
        "CREATE VIEW v_cases AS SELECT case_id, outcome, risk_band FROM cases")
    con.execute(
        "CREATE VIEW v_audit AS SELECT seq, entry_hash FROM audit_log")
    con.commit()
    con.set_authorizer(_authorizer)
    return con


def create_seeded_store(customers, cases) -> sqlite3.Connection:
    """Build the store, seed it, then install the authorizer."""
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE TABLE customers (customer_id TEXT PRIMARY KEY, "
        "full_name TEXT, country TEXT, risk_band TEXT)")
    con.execute(
        "CREATE TABLE cases (case_id TEXT PRIMARY KEY, customer_id TEXT, "
        "outcome TEXT, risk_band TEXT)")
    con.execute(
        "CREATE TABLE audit_log (seq INTEGER PRIMARY KEY, entry_hash TEXT, "
        "prev_hash TEXT, payload TEXT)")
    con.execute(
        "CREATE VIEW v_customers AS SELECT customer_id, country, risk_band "
        "FROM customers")
    con.execute(
        "CREATE VIEW v_cases AS SELECT case_id, outcome, risk_band FROM cases")
    con.execute(
        "CREATE VIEW v_audit AS SELECT seq, entry_hash FROM audit_log")
    con.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)
    con.executemany("INSERT INTO cases VALUES (?,?,?,?)", cases)
    con.commit()
    con.set_authorizer(_authorizer)
    return con


def fetch_cases(con: sqlite3.Connection, max_rows: int = MAX_ROWS) -> list:
    """Fetch case rows through the view, capped at fetch time."""
    cur = con.execute("SELECT case_id, outcome, risk_band FROM v_cases")
    rows = cur.fetchmany(max_rows + 1)
    if len(rows) > max_rows:
        raise RowCapExceeded(f"row cap exceeded: more than {max_rows} rows")
    return rows


def fetch_customers(con: sqlite3.Connection, max_rows: int = MAX_ROWS) -> list:
    cur = con.execute("SELECT customer_id, country, risk_band FROM v_customers")
    rows = cur.fetchmany(max_rows + 1)
    if len(rows) > max_rows:
        raise RowCapExceeded(f"row cap exceeded: more than {max_rows} rows")
    return rows
