from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from office365.sharepoint.client_context import ClientContext
from pytest import fixture


ROOT = Path(__file__).parents[1]
load_dotenv(ROOT/'.env')

@fixture(scope='session')   # function, class, module, package, session
def a_site():       # ProcesamientoMediosdePago 
    return "https://bineomex.sharepoint.com/sites/Data-Prod/"

@fixture(scope='session') 
def a_user(): 
    return getenv('SHARE_USER')

@fixture(scope='session') 
def a_password(): 
    return getenv('SHARE_PASS')

@fixture(scope='session') 
def a_context(a_site, a_user, a_password): 
    return ClientContext(a_site).with_user_credentials(a_user, a_password)

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

