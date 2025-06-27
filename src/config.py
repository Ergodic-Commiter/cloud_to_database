
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

ROOT_DIR = Path(__file__).parents[1]
load_dotenv(ROOT_DIR/'.env')


sqlserver = 'fiserv-reports'
sqldatabase = 'fiserv-db'


def user365(): 
    return SecretStr(getenv('SHARE_USER'))

def pass365(): 
    return SecretStr(getenv('SHARE_PASS'))

def dbuser(): 
    return getenv('SHARE_USER')

def dbpass():
    return getenv('SHARE_PASS')
