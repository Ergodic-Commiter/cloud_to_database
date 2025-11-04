from typing import Optional
from azure.storage.blob import ContainerClient

from ptlf import core 


def get_container(cfg:Optional[core.Settings]=None): 
    cfg = cfg or core.Settings()
    if not cfg.storage_account_url or not cfg.storage_container: 
        raise ValueError("Missing STORAGE_ACCOUNT_URL or STORAGE_CONTAINER")
    az_creds = cfg.azure_creds()
    container_url = f"{cfg.storage_account_url}/{cfg.storage_container}"
    return ContainerClient.from_container_url(container_url, az_creds)

