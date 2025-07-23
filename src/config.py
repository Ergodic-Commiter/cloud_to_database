from os import getenv
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parents[1]
load_dotenv(ROOT/'.env', override=True)


sqldriver = "{ODBC Driver 18 for SQL Server}"
sqlserver = 'fiserv-reports.database.windows.net'
sqldatabase = 'fiserv-db'


def get_creds(user_type=None):
    user_type = user_type or 'personal'
    cred_keys = ('user', 'password')
    env_keys = {
        'personal': ('AZURE_USER_PERSONAL', 'AZURE_PASS_PERSONAL'),
        'project':  ('AZURE_USER_PROJECT',  'AZURE_PASS_PROJECT'),
        'sp' :      ('AZURE_CLIENT',        'AZURE_SECRET'),
        'sql':      ('AZURE_SQL_USER',      'AZURE_SQL_PASS')}
    if user_type not in env_keys: 
        err_msg = (f"User type '{user_type}' is not valid."
            f"\nChoose one among: {env_keys.keys()}")
        raise ValueError(err_msg)
    return dict(zip(cred_keys, env_keys))


def db_params():
    the_params = dict(Driver=sqldriver, 
        Server=sqlserver, Database=sqldatabase, 
        UID=getenv('AZURE_CLIENT'), PWD=getenv('AZURE_SECRET'), 
        Encrypt='yes', TrustServerCertificate='no', 
        Authentication = 'ActiveDirectoryServicePrincipal')
    return the_params



