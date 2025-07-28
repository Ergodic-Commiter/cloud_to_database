import re

import pandas as pd
from pyodbc import connect
import sqlalchemy as alq
from sqlalchemy.engine import URL
from sqlalchemy.dialects import mssql

from src import config as cfg
from src import db

def _parse_format(fmt_str:str):
    reg_fmt = r"^(S?9|X)(?:\((\d{1,4})\))?(?:V9(\d))?"
    if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
        raise ValueError(f"Format string '{fmt_str}' cannot be parsed.")        
    base0, len0, v9 = reg_match.groups()
    if base0 == 'X':
        return mssql.VARCHAR(int(len0 or 1))
    if base0 in ('9', 'S9'):
        len1 = int(len0 or 1)
        dec1 = int(v9 or 0)
        prec = len1 + dec1
        scale = dec1 
        return mssql.DECIMAL(prec, scale)
    raise ValueError(f"Format string '{fmt_str}' cannot parse base '{base_type}'.")


def row_to_colspec(t_row:tuple, description=True):
    _cols = ['Name1', 'Format', 'Description']
    
    try: 
        r_name = t_row.Name1    # Matches λ_mutate below.  
        r_format = _parse_format(t_row.Format)
        r_comment = t_row.Description if description else None
        return alq.Column(r_name, r_format, comment=r_comment)
    except Exception as e: 
        e_msg = f"Error with row: {t_row}\n\nOriginal error: {e}"
        raise ValueError(e_msg) from e
    

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
        Authentication = auths.get(user_type) or auths[...])
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
        

def get_engine(): 
    db_params = get_params()
    conn_str = ''.join('{}={};'.format(*k_v) 
            for k_v in db_params.items())
    conn_qry = {'odbc_connect': conn_str}
    conn_url = URL.create('mssql+pyodbc', query=conn_qry)
    alq_engine = alq.create_engine(conn_url)
    # engine = fz.pipe(cfg.db_params().items(), 
    #     partial2(starmap, "{}={};".format), ''.join, 
    #     partial2(dict, odbc_connect=...), 
    #     partial2(URL.create, "mssql+pyodbc", query=...), 
    #     alq.create_engine)    
    return alq_engine
