"""Authorizer tests.

IMPORTANT: these tests assert on the exception TYPE only (DatabaseError
or a subclass). They never assert on error message text, because the
authorizer's denial text is an implementation detail of SQLite, not a
contract of this repo. That is what "text check disabled" means here.
"""

import sqlite3

import pytest

from kyc_aml.store import (RowCapExceeded, create_seeded_store,
                           create_store, fetch_cases, fetch_customers)


def seeded():
    customers = [("C1", "A", "low-risk-land", "low"),
                 ("C2", "B", "low-risk-land", "low"),
                 ("C3", "C", "low-risk-land", "low")]
    cases = [("K1", "C1", "approve", "low"),
             ("K2", "C2", "human_review", "medium"),
             ("K3", "C3", "approve", "low")]
    return create_seeded_store(customers, cases)


def test_direct_base_table_read_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("SELECT * FROM customers").fetchall()


def test_direct_cases_table_read_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("SELECT * FROM cases").fetchall()


def test_direct_audit_table_read_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("SELECT * FROM audit_log").fetchall()


def test_sqlite_master_read_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("SELECT name FROM sqlite_master").fetchall()


def test_view_read_allowed():
    con = seeded()
    rows = con.execute("SELECT * FROM v_cases").fetchall()
    assert len(rows) == 3


def test_view_read_exposes_no_pii_columns():
    con = seeded()
    cols = [d[0] for d in
            con.execute("SELECT * FROM v_customers").description]
    assert "full_name" not in cols
    assert "email" not in cols


def test_insert_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("INSERT INTO customers VALUES ('X','Y','Z','low')")


def test_update_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("UPDATE cases SET outcome='approve' WHERE case_id='K1'")


def test_delete_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("DELETE FROM cases WHERE case_id='K1'")


def test_pragma_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("PRAGMA table_info(customers)").fetchall()


def test_attach_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("ATTACH ':memory:' AS other")


def test_create_table_denied():
    con = seeded()
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("CREATE TABLE evil (x TEXT)")


def test_fetch_cases_row_cap_enforced_at_fetch_time():
    con = seeded()
    with pytest.raises(RowCapExceeded):
        fetch_cases(con, max_rows=2)


def test_fetch_cases_within_cap_returns_rows():
    con = seeded()
    assert len(fetch_cases(con, max_rows=10)) == 3


def test_fetch_customers_row_cap_enforced():
    con = seeded()
    with pytest.raises(RowCapExceeded):
        fetch_customers(con, max_rows=2)


def test_empty_store_view_read_allowed():
    con = create_store()
    assert con.execute("SELECT * FROM v_cases").fetchall() == []
