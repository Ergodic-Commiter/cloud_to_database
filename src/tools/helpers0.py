from pathlib import Path
from platform import system
import re
from typing import Union


def shortcut_target(a_file:Union[str,Path], **kwargs):
    a_file = Path(a_file)
    if a_file.is_symlink(): 
        return a_file.resolve()
    if system() == 'Windows' and a_file.suffix == '.lnk': 
        return _windows_shortcut(a_file, kwargs.get('file_ext'))
    if system() == 'Darwin': 
        return _mac_alias(a_file)
    raise ValueError("Nor a recognized shortcut or symlink.")

def _mac_alias(a_file:Path): 
    from mac_alias import read_alias
    with a_file.open('rb') as _f: 
        return read_alias(_f).path

def _windows_shortcut(a_file:Path, file_ext:str=None):
    if file_ext is None:
        if isinstance(a_file, WindowsPath):
            file_ext = re.findall(r"\.([A-Za-z]{3,4})\.lnk", a_file.name)[0]
        else:
            raise Exception("Couldn't determine file extension.")
    file_regex = fr'(C:\\.*\.{file_ext})'
    with open(a_file, 'r', encoding='ISO-8859-1') as _f:
        a_path = re.findall(file_regex, _f.read(), flags=re.DOTALL)
    if len(a_path) != 1:
        raise Exception('Not unique or no shortcut targets found in link.')
    return a_path[0]

def _windows_shortcut_2(a_file:Path): 
    from pylnk3 import parse
    with a_file.open('rb') as _f: 
        return Path(parse(f).path)

def str_camel_to_snake(a_str:str): 
    raise NotImplementedError("Function 'str_camel_to_snake' is not implemented.")