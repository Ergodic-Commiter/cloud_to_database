from pathlib import Path
import typer

from ptlf import run

app = typer.Typer()

@app.command()
def update_specs(): 
    pass 

@app.command()
def setup_database(): 
    pass 

@app.command()
def upload_data(filename:Path, *, debug=False): 
    run.from_path(filename, debug=debug)
 
def main():
    app()


    


