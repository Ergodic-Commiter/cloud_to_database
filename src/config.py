import os
from pathlib import Path
from tempfile import gettempdir
from typing import Literal, Optional, Tuple

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.ptlf import errors as ee
# pylint: disable=too-few-public-methods


class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    env: str = Field(default='dev', alias='PTLF_ENV')
    data_loc: Optional[Path] = None  # Se configura en model_post_init
    xl_ref: Tuple[Path, str, str] = (Path('data/PTLF-cols-1.xlsx'), 'LO', 'ptlf_cols')
    
    # Azure Service Principal
    tenant_id: Optional[str] = Field(None, alias='AZURE_TENANT_ID')
    subscription_id: Optional[str] = Field(None, alias='AZURE_SUBSCRIPTION_ID')
    client_id: Optional[str] = Field(None, alias='AZURE_CLIENT_ID')
    client_secret: Optional[str] = Field(None, alias='AZURE_CLIENT_SECRET')
    
    # Azure Resources
    storage_account_url: Optional[str] = Field(None, alias='STORAGE_ACCOUNT_URL')
    storage_container: Optional[str] = Field(None, alias='STORAGE_CONTAINER')
    sql_driver: Optional[str] = "{ODBC Driver 18 for SQL Server}"  # Configurar el driver. 
    sql_server: Optional[str] = Field(None, alias='SQL_SERVER')
    sql_database: Optional[str] = Field(None, alias='SQL_DATABASE')
    registry_container: Optional[str] = Field(None, alias='AZURE_CONTAINER')
    
    # Other credentials
    sql_user: Optional[str] = Field(None, alias='SQL_USER')
    sql_password: Optional[str] = Field(None, alias='SQL_PASSWORD')
    
    # Sandbox stuff
    onedrive_path: Optional[str] = Field(None, alias='ONEDRIVE_PATH')
    my_user: Optional[str] = Field(None, alias='AZURE_USER_PERSONAL')
    my_password: Optional[str] = Field(None, alias='AZURE_PASS_PERSONAL')
    proj_user: Optional[str] = Field(None, alias='AZURE_USER_PROJECT')
    proj_password: Optional[str] = Field(None, alias='AZURE_PASSWORD_PROJECT')
    client_test: Optional[str] = Field(None, alias='AZURE_CLIENT_TEST')
    secret_test: Optional[str] = Field(None, alias='AZURE_SECRET_TEST')
    scope_test: Optional[str] = Field(None, alias='AZURE_SCOP_TEST')
    sp_name: Optional[str] = Field(None, alias='AZURE_SP_NAME')
    sp_id: Optional[str] = Field(None, alias='AZURE_SP_ID')
    dev_login: Optional[str] = Field(None, alias='AZURE_SQL_LOGIN')
    dev_password: Optional[str] = Field(None, alias='AZURE_SQL_PASS2')
    sql_string: Optional[str] = Field(None, alias='STRING_SQL')
    sql_entra: Optional[str] = Field(None, alias='STRING_ENTRA')
    sql_entra_int: Optional[str] = Field(None, alias='STRING_ENTRA_INT')

    def get_creds(self, user_type=None): 
        user_type = user_type or 'personal'
        cred_keys = ('user', 'password')
        env_names = dict(
            personal = (self.my_user, self.my_password),
            project = (self.proj_user, self.proj_password),
            entra = (self.proj_user, self.proj_password),
            sql = (self.sql_user, self.sql_password),
            sp = (self.client_id, self.client_secret))
        if user_type not in env_names: 
            raise ee.KeyCredentialsError(user_type, 'user-password')
        env_vals = [os.environ[nm] for nm in env_names[user_type]]
        return dict(zip(cred_keys, env_vals))

    def azure_creds(self, user_type:Literal['default', 'sp']='default'): 
        if user_type == 'default': 
            return DefaultAzureCredential()
        if user_type == 'sp': 
            env_keys = dict(tenant_id=self.tenant_id, 
                subscription_id=self.subscription_id, 
                client_secret=self.client_secret,
                client_id=self.client_id)
            return ClientSecretCredential(**env_keys) 
        raise ee.KeyCredentialsError(user_type, 'Azure')
    
    def model_post_init(self, context):
        if self.data_loc is None:
            is_auto = self.env in {'prod', 'azure'}
            self.data_loc = Path(gettempdir()) if is_auto else Path("data/temp")
        return 

