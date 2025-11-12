from datetime import datetime as dt
from pathlib import Path
import typer 

from ptlf import services
from ptlf.core import models 


app = typer.Typer(help="Main PTLF CLI", no_args_is_help=True)

data_app = typer.Typer(help="for the data lifecycle")
app.add_typer(data_app, name='data')

user_app = typer.Typer(help="for setting client users up")
app.add_typer(user_app, name='user')

infra_app = typer.Typer(help="for setting infrastructure resources up")
# Not yet implemented.


### Data Group

@data_app.command('upload')
def upload_data(filename:Path, *, debug=False): 
    services.upload_data(filename, debug=debug)

@data_app.command('status')
def check_status(): 
    status_df = services.check_status()
    print_df = status_df.to_csv(sep='\t', index=False)
    print(print_df)

@data_app.command('reload')
def reload_data(filename:Path, *, debug=False): 
    services.reload_data(filename, debug=debug)

@data_app.command('delete')
def delete_date(a_date:dt, *, debug=False):
    services.delete_date(a_date, debug=debug)


### User Group

@user_app.command('reload-specs')
def reload_specs():
    models.reload_specs()
  
@user_app.command('create-view')
def create_view(user_col:str):
    services.create_view(user_col)

@user_app.command('create-pqms')
def create_pqms(user_col:str, path_to:Path=None): 
    services.create_pqms(user_col, path_to)


### Init Group: Not yet implemented

@infra_app.command()
def setup_database(): 
    pass


