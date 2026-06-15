from datetime import datetime as dt
from pathlib import Path
from typing import Annotated

from rich.traceback import install as rich_install
from typer import Typer, Option
from ptlf import services

data_app = Typer(help="for the data lifecycle")

@data_app.command('upload')
def upload_data(filename:Path, *, debug=False): 
    services.upload_data(filename, debug=debug)


def parse_query(value:str) -> int|str: 
    try: 
        return int(value)
    except ValueError: 
        return value

@data_app.command('status')
def check_status(query:Annotated[str|None, Option('--query', '-q')]=None): 
    rich_install(show_locals=False)
    parsed = parse_query(query) if query else None
    status_df = services.check_status(parsed)
    print_df = status_df.to_csv(sep='\t', index=False)
    print(print_df)


@data_app.command('reload')
def reload_data(filename:Path, *, debug=False): 
    services.reload_data(filename, debug=debug)


@data_app.command('delete')
def delete_date(a_date:dt, *, debug=False):
    services.delete_date(a_date, debug=debug)
