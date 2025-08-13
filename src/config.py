import os
from pathlib import Path

from azure.identity import ClientSecretCredential
from dotenv import load_dotenv
from toolz import dicttoolz as dz

from src.tools import partial2

ROOT = Path(__file__).parents[1]
load_dotenv(ROOT/'.env', override=True)

XL_REF = ('data/PTLF-cols.xlsx', 'LO', 'ptlf_cols')


def get_creds(user_type=None):
    user_type = user_type or 'personal'
    cred_keys = ('user', 'password')
    env_names = dict(
        personal = ('AZURE_USER_PERSONAL', 'AZURE_PASS_PERSONAL'),
        project = ('AZURE_USER_PROJECT', 'AZURE_PASSWORD_PROJECT'),
        entra = ('AZURE_USER_PROJECT', 'AZURE_PASSWORD_PROJECT'),
        sql = ('AZURE_USER_SQL', 'AZURE_PASS_SQL'),
        sp = ('AZURE_SP_CLIENT', 'AZURE_SP_SECRET'))
    if user_type not in env_names: 
        err_msg = (f"User type '{user_type}' must be one of {list(env_names.keys())}")
        raise ValueError(err_msg)
    env_vals = [os.environ[nm] for nm in env_names[user_type]]
    return dict(zip(cred_keys, env_vals))


def azure_creds(user_type=None): 
    user_type = user_type or 'sp'
    valid_types = {'sp'}
    if user_type not in valid_types: 
        raise ValueError(f"User type '{user_type}' not from {valid_types}")
    if user_type == 'sp': 
        env_keys = dict(tenant_id='AZURE_TENANT', 
            subscription_id='AZURE_SUBSCRIPTION_TEST', 
            client_secret='AZURE_SP_SECRET',
            client_id='AZURE_SP_CLIENT')
        creds = dz.valmap(lambda vv: os.environ[vv], env_keys)
        return ClientSecretCredential(**creds) 
