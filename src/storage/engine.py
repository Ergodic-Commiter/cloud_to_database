from azure.storage.blob import ContainerClient

from src import config as cfg, storage as stg 


def get_container(): 
    stg_url = f"https://{stg.storage}.blob.core.windows.net/{stg.container}"
    az_creds = cfg.azure_creds()
    az_container = ContainerClient.from_container_url(stg_url, az_creds)
    return az_container

