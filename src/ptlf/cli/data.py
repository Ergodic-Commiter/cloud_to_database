from datetime import datetime as dt
from pathlib import Path

from rich.traceback import install as rich_install
import typer
from ptlf import services

data_app = typer.Typer(help="for the data lifecycle")

@data_app.command('upload')
def upload_data(filename:Path, *, debug=False): 
    services.upload_data(filename, debug=debug)

@data_app.command('status')
def check_status(): 
    rich_install(show_locals=False)
    status_df = services.check_status()
    print_df = status_df.to_csv(sep='\t', index=False)
    print(print_df)

@data_app.command('reload')
def reload_data(filename:Path, *, debug=False): 
    services.reload_data(filename, debug=debug)

@data_app.command('delete')
def delete_date(a_date:dt, *, debug=False):
    services.delete_date(a_date, debug=debug)
