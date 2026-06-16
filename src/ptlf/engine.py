import ibis
import pyodbc 
import sqlalchemy as alq
from sqlalchemy.engine import URL
from toolz import dicttoolz as dz

from ptlf.core import errors as ee, settings as ss
# pylint:disable=c-extension-no-member

def get_params(cfg:ss.Settings=None, user_type:str='sp'):
    cfg = cfg or ss.config
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
    db_params = get_params(user_type=user_type)
    conn_str = ''.join(f'{k}={v};' for k,v in db_params.items())
    if conn_type == 'pyodbc': 
        return pyodbc.connect(conn_str)
    if conn_type == 'sqlalchemy': 
        conn_query = dict(odbc_connect=conn_str)
        conn_url = alq.engine.URL.create("mssql+pyodbc", query=conn_query)
        return alq.create_engine(conn_url).connect()
    if conn_type == 'ibis': 
        ibis_keys = dict(UID='user', PWD='password', Server='host', 
            Database='database', Driver='driver')
        λ_ibis = lambda kk: ibis_keys.get(kk, kk) 
        ibis_params = dz.keymap(λ_ibis, db_params) 
        return ibis.mssql.connect(**ibis_params)
    raise ee.KeyCredentialsError(conn_type, 'Conexión base de datos')
        

def get_engine(cfg:ss.Settings, **kwargs) -> alq.Engine: 
    db_params = get_params(cfg)
    conn_str = ''.join('{}={};'.format(*k_v) 
            for k_v in db_params.items())
    conn_qry = {'odbc_connect': conn_str}
    conn_url = URL.create('mssql+pyodbc', query=conn_qry)
    return alq.create_engine(conn_url, **kwargs)



    
