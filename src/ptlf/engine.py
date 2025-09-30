from operator import attrgetter as ɑ
from pathlib import Path
from typing import Literal

# pylint:disable=no-name-in-module
from pyodbc import connect 
import sqlalchemy as alq
from sqlalchemy.engine import URL

from src import ptlf
from src.ptlf import errors as ee
from src.config import Settings


def get_params(cfg:Settings, 
    user_type:Literal['personal', 'project', 'entra', 'sql', 'sp']='sp'):
    cfg = cfg or Settings()
    user_creds = cfg.get_creds(user_type)
    auths = dict(
        personal = 'ActiveDirectoryPassword', 
        project = 'ActiveDirectoryPassword', 
        entra = 'ActiveDirectoryInteractive', 
        sql = 'SqlPassword',
        sp = 'ActiveDirectoryServicePrincipal')
    if user_type not in auths: 
        raise ee.KeyCredentialsError(user_type, 'Usuario en base de datos')
    params = dict(
        Driver=cfg.sql_driver, 
        Server=cfg.sql_server_url, 
        Database=cfg.sql_database, 
        UID=user_creds['user'], 
        PWD=user_creds['password'], 
        Encrypt='yes', 
        TrustServerCertificate='no', 
        Authentication = auths.get(user_type))
    return params


def get_connection(user_type='sp', conn_type='sqlalchemy'):
    db_params = get_params(user_type)
    conn_str = ''.join('{}={};'.format(*k_v) for k_v in db_params.items())
    # ... join(map(star("{}={};".format), db_params.items())))
    if conn_type == 'pyodbc': 
        return connect(conn_str) 
    if conn_type == 'sqlalchemy': 
        conn_query = dict(odbc_connect=conn_str)
        conn_url = alq.engine.URL.create("mssql+pyodbc", query=conn_query)
        return alq.create_engine(conn_url).connect()
    raise ee.KeyCredentialsError(conn_type, 'Conexión base de datos')
        

def get_engine(cfg:Settings, **kwargs): 
    db_params = get_params(cfg)
    conn_str = ''.join('{}={};'.format(*k_v) 
            for k_v in db_params.items())
    conn_qry = {'odbc_connect': conn_str}
    conn_url = URL.create('mssql+pyodbc', query=conn_qry)
    return alq.create_engine(conn_url, **kwargs)


def make_query(cfg:Settings, by_col=None, to_file=Path): 
    by_col = by_col or 'AliasToken'
    to_file = Path(to_file)

    ptlf_specs = ptlf.typer.read_specs(output='dataframe')
    if by_col not in ptlf_specs.columns: ## Se cambió PTLF_SPECS de data_frame a diccionario.  
        raise ee.SpecsPTLF_Error(by_col)

    meta = alq.MetaData()
    alq_eng = get_engine(cfg)
    ptlf_tbl = alq.Table('PTLF_raw', meta, schema='dbo', autoload_with=alq_eng)
    def λ_sqlcol(row): 
        name, label = ɑ('Name1', by_col)(row)
        return ptlf_tbl.c[name].label(label)

    new_specs = ptlf_specs[~ptlf_specs[by_col].isnull()]
    alq_stmt = alq.select(*map(λ_sqlcol, new_specs.itertuples()))
    sql_stmt = (alq_stmt.compile(alq_eng, compile_kwargs=dict(literal_binds=True))
        .string.replace(', dbo', ',\n\tdbo'))
    Path(to_file).write_text(sql_stmt, encoding='utf8')
    


    
