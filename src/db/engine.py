from operator import attrgetter as ɑ, methodcaller as ρ
from pathlib import Path
import re
from warnings import warn

import pandas as pd
from pyodbc import connect  # pylint:disable=no-name-in-module
from toolz import functoolz as fz
import sqlalchemy as alq
from sqlalchemy.engine import URL

from src import config as cfg, db, tools
from src.db.typer import TypeManager


def _format_groups(fmt_str:str): 
    # COBOL: (S?9|X)\((\d+)\)(V9(9|\(\d\)))?
    # S9(n), 9(n), X(n), S9(n)V9(k), 9(n)V99... 
    reg_fmt = r"^(S?9|X)(?:\((\d{1,4})\))(?:V9(\d))?"
    if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
        raise ValueError(f"Format string '{fmt_str}' cannot be parsed.")        
    return reg_match.groups()


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
    if conn_type == 'sqlalchemy': 
        conn_query = dict(odbc_connect=conn_str)
        conn_url = alq.engine.URL.create("mssql+pyodbc", query=conn_query)
        return alq.create_engine(conn_url).connect()
    
    raise ValueError(f"Conn type {conn_type} is not {{pyodbc, sqlalchemy}}")
        

def get_engine(fast_exec=False): 
    db_params = get_params()
    conn_str = ''.join('{}={};'.format(*k_v) 
            for k_v in db_params.items())
    conn_qry = {'odbc_connect': conn_str}
    conn_url = URL.create('mssql+pyodbc', query=conn_qry)
    return alq.create_engine(conn_url, fast_executemany=fast_exec)


def read_specs():
    λ_mutate = dict(
        Name0 = lambda df: df['Field Name'].str.replace(' ', ''), 
        Name1 = lambda df: index_duplicates(df['Name0']), 
        Format = lambda df: df['Format'].str.replace(' ', ''))
    specs_ref = tools.OpenTable(*cfg.XL_REF)
    specs_df = specs_ref.get_dataframe().assign(**λ_mutate)
    return specs_df


def attrs_to_df(specs_0):
    attrs = list(map(TypeManager.from_specs, specs_0.itertuples()))
    meta = dict(
        Name0=ɑ('_specs._3'),  # corresponds to "Field Name"
        Name1=ɑ('specs.Name1'), 
        pytype=ɑ('pytype.__name__'), 
        mssql=fz.compose_left(ρ('mssql_col'), str))
    λ_meta = fz.juxt(*meta.values())
    attrs_data = list(map(λ_meta, attrs))
    return pd.DataFrame(attrs_data, columns=list(meta.keys()))


def specs_to_excel(specs_1): 
    file, sheet, table = cfg.XL_REF
    specs_ref = tools.OpenTable(file, sheet, table)
    _, min_row, max_col, _ = specs_ref.boundaries
    writer_args = dict(engine='openpyxl', mode='a', if_sheet_exists='overlay')  
    excel_args = dict(sheet_name=sheet, startrow=min_row-1, startcol=max_col+1, 
        header=True, index=False)
    with pd.ExcelWriter(file, **writer_args) as xl:
        specs_1.to_excel(xl, **excel_args)    


def check_lengths(file, mode='latin1'):
    with open(file, 'r', encoding='latin1') as f:
        lengths = list(map(len, f))
    l0 = lengths[0]
    assert all(ll == l0 for ll in lengths),\
        f"Lines in '{file}' with mode '{mode}' have different lengths."
    return l0


def trim_file(a_file, length): 
    a_file = Path(a_file)
    trim_2 = a_file.parents[1]/'trim'/a_file.name
    λ_trim = lambda ll: ll[:length]+b'\n'
    with open(a_file, 'rb') as r, open(trim_2, 'wb') as w: 
        for line in r: 
            w.write(λ_trim(line))
    return str(trim_2)


def read_ptlf(file):
    ptlf_specs = read_specs()
    len_0 = ptlf_specs.Length.sum()
    len_1 = check_lengths(file)
    if len_1 != len_0: 
        warn(f"Length of lines {len_1} doesn't correspond to specifications {len_0}")
        file = trim_file(file, len_0)

    ptlf_attrs = map(TypeManager.from_specs, ptlf_specs.itertuples())
    ptlf_types = dict((attr.specs.Name1, attr.pytype) for attr in ptlf_attrs)
    pre_df = pd.read_fwf(file, encoding='latin1', 
        widths=ptlf_specs.Length, names=ptlf_specs.Name1, na_filter=False)
    return pre_df.astype(ptlf_types)

    