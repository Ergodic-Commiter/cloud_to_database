
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

ROOT = Path(__file__).parents[1]
load_dotenv(ROOT/'.env')


sqlserver = 'fiserv-reports.database.windows.net'
sqldatabase = 'fiserv-db'
sqldriver = "{ODBC Driver 18 for SQL Server}"

def user365(): 
    return SecretStr(getenv('SHARE_USER'))

def pass365(): 
    return SecretStr(getenv('SHARE_PASS'))

def dbuser(): 
    return getenv('SHARE_USER')

def dbpass():
    return getenv('SHARE_PASS')
