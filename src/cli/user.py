from pathlib import Path
import typer
from ptlf import services
from ptlf.core import specs as spx

user_app = typer.Typer(help="for setting client users up")

user_app.command('reload-specs')
def reload_specs():
    spx.reload_specs()
  
@user_app.command('create-view')
def create_view(user_col:str):
    services.create_view(user_col)

@user_app.command('create-pqms')
def create_pqms(user_col:str, path_to:Path=None): 
    services.create_pqms(user_col, path_to)

@user_app.command('create')
def create_user(name:str, password:str): 
    services.create_user(name, password)

