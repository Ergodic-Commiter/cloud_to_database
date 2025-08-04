from io import StringIO
from operator import attrgetter as ɑ, itemgetter as ɣ
import re

import pandas as pd
from pyodbc import connect
from toolz import functoolz as fz
import sqlalchemy as alq
from sqlalchemy.engine import URL
from sqlalchemy.dialects import mssql

from src import config as cfg, db, tools
from src.db.typer import TypeManager


def _format_groups(fmt_str:str): 
    # COBOL: (S?9|X)\((\d+)\)(V9(9|\(\d\)))?
    # S9(n), 9(n), X(n), S9(n)V9(k), 9(n)V99... 
    reg_fmt = r"^(S?9|X)(?:\((\d{1,4})\))(?:V9(\d))?"
    if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
        raise ValueError(f"Format string '{fmt_str}' cannot be parsed.")        
    return reg_match.groups()

# mssql types: 
# Exact: tinyint, smallint, int, bigint, bit, decimal, numerical, 
#   money, smallmoney
# Approximate: float, real
# Date & Time: date, time, datetime2, datetimeoffset, datetime, smalldatetime
# Char Strings: char, varchar, text
# Unicode Char Strings: nchar, nvarchar, ntext
# Binary Strings: binary, varbinary, image
# Other: cursor, geography, geometry, hierarchyid, json, vector, rowversion, 
#   sql_variant, table, uniqueidentifier, xml


def index_duplicates(srs:pd.Series):
    duplicates = srs.duplicated(False)
    occurrence = srs.groupby(srs).cumcount() + 1
    suffix = ('_' + occurrence.astype(str)).where(duplicates, '')
    return srs+suffix


def get_params(user_type='sp'):
    user_creds = cfg.get_creds(user_type)
    auths = dict(
        personal = 'ActiveDirectoryPassword', 
        project = 'ActiveDirectoryPassword', 
        entra = 'ActiveDirectoryInteractive', 
        sql = 'SqlPassword',
        sp = 'ActiveDirectoryServicePrincipal')
    if user_type not in auths: 
        e_msg = (f"User type {user_type} must be one of:\n{list(auths.keys())}")
        raise ValueError(e_msg)
    params = dict(
        Driver=db.sqldriver, 
        Server=db.sqlserver, 
        Database=db.sqldatabase, 
        UID=user_creds['user'], 
        PWD=user_creds['password'], 
        Encrypt='yes', 
        TrustServerCertificate='no', 
        Authentication = auths.get(user_type))
    return params


def get_connection(user_type='sp', conn_type='sqlalchemy'):
    db_params = get_params(user_type)
    conn_str = ''.join('{}={};'.format(*k_v) for k_v in db_params.items())
    if conn_type == 'pyodbc': 
        return connect(conn_str) 
    
    elif conn_type == 'sqlalchemy': 
        conn_query = dict(odbc_connect=conn_str)
        conn_url = alq.engine.URL.create("mssql+pyodbc", query=conn_query)
        return alq.create_engine(conn_url).connect()
        

def get_engine(fast_exec=False): 
    db_params = get_params()
    conn_str = ''.join('{}={};'.format(*k_v) 
            for k_v in db_params.items())
    conn_qry = {'odbc_connect': conn_str}
    conn_url = URL.create('mssql+pyodbc', query=conn_qry)
    return alq.create_engine(conn_url, fast_executemany=fast_exec)


def read_specs(table):
    if table == 'ptlf': 
        xl_ref = ('data/PTLF-cols.xlsx', 'LO', 'ptlf_cols')
        λ_mutate = dict(
            Name0 = lambda df: df['Field Name'].str.replace(' ', ''), 
            Name1 = lambda df: index_duplicates(df['Name0']), 
            Format = lambda df: df['Format'].str.replace(' ', ''))
    return tools.read_excel_table(*xl_ref).assign(**λ_mutate)


def read_ptlf(file_name, read_via='text'):
    if read_via == 'text': 
        file_or_buffer = file_name
    if read_via == 'io': 
        rec_len = 10001
        with open(file_name, 'r', encoding='latin1') as f: 
            content = f.read()
            assert len(content) % rec_len == 0
            lines = [content[i:i+rec_len] for i in range(0, len(content), rec_len)]
        buffer = StringIO("\n".join(lines))
        file_or_buffer = file_name

    ptlf_specs = read_specs('ptlf')
    ptlf_attrs = list(map(TypeManager.from_specs, ptlf_specs.itertuples()))
    ptlf_types = dict((attr.specs.Name1, attr.pytype) for attr in ptlf_attrs)
    pre_df = pd.read_fwf(file_or_buffer, encoding='latin1', 
        widths=ptlf_specs.Length, names=ptlf_specs.Name1)
    return pre_df.apply(ptlf_types)


def clean_binaries(a_df): 
    # λ_decode = (lambda x: x if not isinstance(x, bytes) 
            # else x.decode('utf-8', errors='replace')) 
            # lambda X: X.apply(λ_decode)
    Λ_replace = lambda X: X.astype(str).str.replace('\x00', '', regex=False)
    obj_cols = a_df.select_dtypes(include='object').columns
    a_df[obj_cols] = a_df[obj_cols].apply(Λ_replace)
    return a_df
