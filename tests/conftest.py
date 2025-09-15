
from office365.sharepoint.client_context import ClientContext
from pytest import fixture

from src.ptlf import engine

# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable

# Parser options. 
def pytest_addoption(parser):
    user_type = dict(name='--user-type', 
        action='store', default='sp', 
        help="User type: [personal, project, entra, sql, sp]")
    conn_type = dict(name='--conn-type', 
        action='store', default='pyodbc', 
        help="Connection type: [pyodbc, sqlalchemy]")
    for opt_dict in (user_type, conn_type): 
        name = opt_dict.pop('name')
        parser.addoption(name, **opt_dict)
    return 

# The fixtures: 
@fixture(scope='session')
def user_type(request): 
    return request.config.getoption('--user-type')

@fixture(scope='session')
def conn_type(request): 
    return request.config.getoption('--conn-type')

@fixture(scope='session')
def conn_fixture(user_type, conn_type): 
    with engine.get_connection(user_type, conn_type) as conn: 
        yield conn



## Estos eran para experimentos de Sharepoint, pero ya no los usamos. 
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
    