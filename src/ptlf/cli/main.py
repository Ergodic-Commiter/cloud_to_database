from pathlib import Path

import typer 

from ptlf import services
from ptlf.core import models 



app = typer.Typer()

@app.command()
def reload_specs():
    models.reload_specs()
     
@app.command()
def setup_database(): 
    pass 

@app.command()
def upload_data(filename:Path, *, debug=False): 
    services.upload_data(filename, debug=debug)

@app.command()
def check_status(): 
    status_df = services.check_status()
    print_df = status_df.to_csv(sep='\t', index=False)
    print(print_df)

@app.command()
def create_view(from_col:str):
    services.create_view(from_col)

def main():
    app()


    


