from pytest import mark
import sqlalchemy as alq

from src.db import engine

χ_module = lambda obj, m_str: m_str in type(obj).__module__


def run_single_query(conn, query=None): 
    query = query or 'SELECT 1'
    if χ_module(conn, 'sqlalchemy'): 
        return conn.execute(alq.text(query)).scalar()
    if χ_module(conn, 'pyodbc'): 
        cursor = conn.cursor()
        cursor.execute(query)
        scalar = cursor.fetchone()[0]
        return scalar
    raise ValueError("Connection module must have [pyodbc, sqlalchemy]")


@mark.parametrize('user_type', ['sql', 'sp'])
def test_sqlalchemy_connection(user_type):
    conn = engine.get_connection(user_type, 'sqlalchemy')
    result = run_single_query(conn, "SELECT 1")
    assert result == 1

@mark.parametrize('user_type', ['sql', 'sp'])
def test_pyodbc_connection(user_type):
    conn = engine.get_connection(user_type, 'pyodbc')
    result = run_single_query(conn, "SELECT 1")
    assert result == 1

