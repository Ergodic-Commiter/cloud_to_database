
from pathlib import Path
from office365.sharepoint.client_context import ClientContext
from .config import user365, pass365

SHARE_URL = "https://bineomex.sharepoint.com/sites/ProcesamientoMediosdePago/"


def context365(): 
    the_user = user365().get_secret_value()
    the_pass = pass365().get_secret_value()
    return ClientContext(SHARE_URL).with_user_credentials(the_user, the_pass)


def download_file(context: ClientContext, path_in, path_out):
    to_path = Path(path_out).parent/Path(path_in).basename
    (context
        .get_file_by_server_relative_path(path_in)
        .download(path_out)
        .execute_query())
    