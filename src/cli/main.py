from rich.traceback import install as rich_install
import typer 

from .data import data_app
from .user import user_app 

rich_install(show_locals=False, max_frames=3, suppress=["click", "typer"])


app = typer.Typer(help="Main PTLF CLI", no_args_is_help=True, 
    pretty_exceptions_enable=True,
    pretty_exceptions_short=True,
    pretty_exceptions_show_locals=False)
app.add_typer(data_app, name='data')
app.add_typer(user_app, name='user')


if __name__ == "__main__": 
    app()