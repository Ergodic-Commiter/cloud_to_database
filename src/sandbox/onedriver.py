import io

import joblib
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from openpyxl import load_workbook
import pandas as pd

from ptlf import core 
# pylint: disable=inconsistent-return-statements
# pylint: disable=invalid-name


def download_from_sharepoint(f_url, context, down_as='pickle'):
    response = File.open_binary(context, f_url)
    bytes_file_obj = io.BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0)
    if down_as == 'pickle': 
        return joblib.load(bytes_file_obj)
    if down_as == 'dataframe': 
        return pd.read_excel(bytes_file_obj, engine='openpyxl')
    if down_as == 'workbook': 
        return load_workbook(bytes_file_obj)
    if down_as == 'csv': 
        io_str = io.StringIO(bytes_file_obj.getvalue().decode())
        return pd.read_csv(io_str)

    

if __name__ == "__main__": 
    creds = core.get_creds('persona')
    site_url = "https://bineomex.sharepoint.com/sites/medios-pago-2/SitePages/ProjectHome.aspx"
    file_url = "/sites/medios-pago-2/_layouts/15/Doc.aspx"
    file_attrs = {'sourcedoc':"{36F6A715-2476-4958-8D5F-1F98A91DD69F}", 
        'file':"Columnas-PTLF.xlsx", 
        'action':"default",
        'mobileredirect': True}

    CTX = ClientContext(site_url).with_credentials(UserCredential(*creds.values()))

    a_df = download_from_sharepoint(file_url, CTX, 'dataframe')
    print(f"The Dataframe has:"
        f"\nSize: {a_df.shape}"
        f"\nColumns: {a_df.columns}")

