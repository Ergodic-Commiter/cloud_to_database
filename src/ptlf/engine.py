import ibis
import pyodbc 
import sqlalchemy as alq
from sqlalchemy.engine import URL
from toolz import dicttoolz as dz

from ptlf.core import errors as ee, settings as ss
# pylint:disable=c-extension-no-member

def get_params(cfg:ss.Settings=None, user_type:str='sp') -> dict:
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


def get_engine(cfg:ss.Settings=None, debug=False, **kwargs) -> alq.Engine: 
    cfg = cfg or ss.config
    defaults = ({} if not debug else 
        dict(fast_executemany=False, echo='debug')) 
    eng_args = defaults | kwargs
    db_params = get_params(cfg)
    conn_str = ''.join('{}={};'.format(*k_v) 
            for k_v in db_params.items())
    conn_qry = {'odbc_connect': conn_str}
    conn_url = URL.create('mssql+pyodbc', query=conn_qry)
    return alq.create_engine(conn_url, **eng_args)

def get_pyodbc(user_type='sp') -> pyodbc.Connection: 
    db_params = get_params(user_type=user_type)
    conn_str = ''.join(f'{k}={v};' for k,v in db_params.items())
    return pyodbc.connect(conn_str)

def get_ibis(user_type='sp') -> ibis.BaseBackend: 
    db_params = get_params(user_type=user_type)
    ibis_keys = dict(UID='user', PWD='password', Server='host', 
        Database='database', Driver='driver')
    λ_ibis = lambda kk: ibis_keys.get(kk, kk) 
    ibis_params = dz.keymap(λ_ibis, db_params) 
    return ibis.mssql.connect(**ibis_params)


def get_connection(user_type='sp', conn_type='sqlalchemy', *, debug=False):
    if conn_type == 'sqlalchemy': 
        return get_engine(debug=debug).connect()
    if conn_type == 'pyodbc': 
        return get_pyodbc(user_type)
    if conn_type == 'ibis': 
        return get_ibis()
    raise ee.KeyCredentialsError(conn_type, 'Conexión base de datos')
     

_SessionLocal = alq.orm.sessionmaker(bind=get_engine())

def get_session() -> alq.orm.Session: 
    return _SessionLocal()

    
