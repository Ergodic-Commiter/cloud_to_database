import os
from pathlib import Path
from dotenv import load_dotenv
from src.tools import partial2

ROOT = Path(__file__).parents[1]
load_dotenv(ROOT/'.env', override=True)


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

