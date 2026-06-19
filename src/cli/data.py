from datetime import datetime as dt
from pathlib import Path
from typing import Annotated

from typer import Typer, Option
from ptlf import services

data_app = Typer(help="for the data lifecycle")

@data_app.command('upload')
def upload_data(filename:Path, *, debug=False):
    ingestor = services.Ingestor(debug) 
    ingestor.upload_data(filename)


def parse_query(value:str) -> int|str: 
    try: 
        return int(value)
    except ValueError: 
        return value

@data_app.command('status')
def check_status(query:Annotated[str|None, Option('--query', '-q')]=None): 
    parsed = parse_query(query) if query else None
    status_df = services.check_status(parsed)
    print_df = status_df.to_csv(sep='\t', index=False)
    print(print_df)


@data_app.command('reload')
def reload_data(filename:Path, *, debug=False):
    ingestor = services.Ingestor(debug)
    ingestor.reload_data(filename)


@data_app.command('delete')
def delete_date(a_date:dt, *, debug=False):
    ingestor = services.Ingestor(debug)
    ingestor.delete_date(a_date)


if __name__ == '__main__': 
    upload_data(Path('data/temp/zips/OneDrive_1_6-17-2026/PRD_TRXS_PTLF_2026-06-15.ZIP'))