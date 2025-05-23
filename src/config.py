
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

ROOT_DIR = Path(__file__).parents[1]
load_dotenv(ROOT_DIR/'.env')


def user365(): 
    return SecretStr(getenv('SHARE_USER'))

def pass365(): 
    return SecretStr(getenv('SHARE_PASS'))




