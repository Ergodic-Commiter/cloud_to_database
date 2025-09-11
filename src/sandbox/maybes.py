# Warnings: 

import warnings
from rich.console import Console

def custom_formatwarning(msg, category, filename, lineno, line=None):
    return f"\033[93m{category.__name__}: {msg}\033[0m\n"

warnings.formatwarning = custom_formatwarning


console = Console()

def rich_formatwarning(msg, category, filename, lineno, line=None):
    return f"[bold yellow]{category.__name__}[/bold yellow]: {msg}\n"

warnings.formatwarning = rich_formatwarning


# Filter warnings. 
warnings.simplefilter("once")   # show each only once
