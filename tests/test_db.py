import sys
from pathlib import Path
from pyodbc import connect 
import sqlalchemy as alq

ε_module = lambda obj, m_str: m_str in type(obj).__module__


def run_single_query(conn, query=None): 
    query = query or 'SELECT 1'
    if ε_module(conn, 'sqlalchemy'): 
        return conn.execute(alq.text(query)).scalar()
    elif ε_module(conn, 'pyodbc'): 
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchone()
    else: 
        raise ValueError("Connection module must have [pyodbc, sqlalchemy]")


def test_connection_alive(db_connection):
    result = run_single_query(db_connection, "SELECT 1")
    assert result[0] == 1

