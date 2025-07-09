from itertools import starmap
from logging import getLogger
from operator import methodcaller as σ, contains
from os import getenv
from pathlib import Path
import sys

from dotenv import load_dotenv
from pyodbc import connect
from pytest import fixture
import sqlalchemy as alq
from toolz import (curried as cz, dicttoolz as dz, functoolz as fz, itertoolz as iz)

from src.tools import partial2, thread 

# Old experiments
from office365.sharepoint.client_context import ClientContext

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT/'src'))
import config as cfg

load_dotenv(ROOT/'.env')

logger = getLogger(__name__)

# Parser options. 
def pytest_addoption(parser):
    user_type = dict(name='--user-type', 
        action='store', default='sp', 
        help="User type: [personal, project]")
    conn_type = dict(name='--conn-type', 
        action='store', default='pyodbc', 
        help="Connection type: [pyodbc, sqlalchemy]")
    
    for opt_dict in (user_type, conn_type): 
        name = opt_dict.pop('name')
        parser.addoption(name, **opt_dict)
    return 


# The fixtures: 
@fixture(scope='session')
def user_creds(request):
    user_type = request.config.getoption("--user-type")
    e_msg = ("Specify '--user-type' from [personal, project, sp] for choosing "
        "credentials from '.env'")
    var_names = ('user', 'password')
    match user_type: 
        case 'personal': 
            env_names = ('AZURE_USER_PERSONAL', 'AZURE_PASS_PERSONAL')
        case 'project' | 'entra': 
            env_names = ('AZURE_USER_PROJECT', 'AZURE_PASSWORD_PROJECT')
        case 'sp': 
            env_names = ('AZURE_CLIENT', 'AZURE_SECRET')
        case '_': 
            raise e_msg
    the_creds = dz.valmap(getenv, 
        dict(zip(var_names, env_names)))
    return the_creds 
   

@fixture(scope='session')
def db_params(user_creds, request):
    user_type = request.config.getoption("--user-type")
    auths = {
        ...: 'ActiveDirectoryPassword',     # Default
        'sp': 'ActiveDirectoryServicePrincipal', 
        'entra': 'ActiveDirectoryInteractive'}
    params = {
        'Driver': cfg.sqldriver, 
        'Server': cfg.sqlserver, 
        'Database': cfg.sqldatabase, 
        'UID': user_creds['user'], 
        'PWD': user_creds['password'],
        'Encrypt': 'yes',
        'TrustServerCertificate': 'no', 
        'Authentication': auths.get(user_type, auths[...])}
    return params


@fixture(scope='session')
def db_connection(db_params, request):
    dict_to_dbstr = fz.compose_left(σ('items'), 
        partial2(starmap, '{}={};'.format), ''.join) 
    # dd ⟼ ''.join( f"{kk}={vv};" for kk, vv in dd.items() )
    conn_type = request.config.getoption("--conn-type")
    match conn_type: 
        case 'pyodbc': 
            conn_str = dict_to_dbstr(db_params)
            logger.info(f"Connection String:\n{conn_str}")
            with connect(conn_str) as conn: 
                yield conn 
        case 'sqlalchemy':  
            conn_str = dict_to_dbstr(db_params)
            with alq.create_engine(eng_str).connect() as conn: 
                yield conn
    return 


## These were for Sharepoint experiments, but aren't used in recent versions. 
@fixture(scope='session')   # function, class, module, package, session
def a_site():       # ProcesamientoMediosdePago 
    return "https://bineomex.sharepoint.com/sites/Data-Prod/"

@fixture(scope='session') 
def a_context(a_site, user_creds): 
    return ClientContext(a_site).with_user_credentials(**user_creds)

@fixture(scope='session')
def a_fileurl(): 
    the_form = 'Forms/AllItems.aspx'
    its_args = dict(
        id = '/'.join(("/sites/ProcesamientoMediosdePago", 
            "Documentos compartidos/Archivos Operativos/PRD/2025/05/16", 
            "PRD_CMS_DAML1001_2025-05-15.ZIP")),
        parent = '/'.join(("/sites/ProcesamientoMediosdePago", 
            "Documentos compartidos/Archivos Operativos/PRD/2025/05/16")),
        sharingv2 = 'true',
        fromShare = 'true',
        at = '9',
        e = '5%3A9a4e2c4ec2624bf2b220ad163dbde59f',
        viewid = 'e256468d-c42e-40d1-a019-43af370dfc81',
        CID = '04fe17c1-c10b-4d1f-a2bc-db9dec3f65a0',
        FolderCTID = '0x01200085CFDC87FD20A14B9884308D89A23C2B')
    return 

@fixture(scope='session')
def local_path(): 
    return "data/temp/download_test.zip"
    