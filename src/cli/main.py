import typer 

from .data import data_app
from .user import user_app 


app = typer.Typer(help="Main PTLF CLI", no_args_is_help=True)
app.add_typer(data_app, name='data')
app.add_typer(user_app, name='user')


