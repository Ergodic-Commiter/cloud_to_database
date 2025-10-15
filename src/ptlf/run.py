from pathlib import Path
import re, zipfile

import sqlalchemy as alq
from ptlf import config, flow, engine, typer

# pylint:disable=redefined-outer-name

RE_PTLF_DAT = re.compile(r"^PTLF_([\d\-]{10})$")
RE_PTLF_ZIP = re.compile(r"^PRD_TRXS_PTLF_([\d\-]{10}).ZIP$")

def _single_run(path:Path, specs:dict, engine:alq.Engine, debug:bool): 
    if RE_PTLF_DAT.match(path.name): 
        the_flow = flow.DayDataFlow.from_data(path, debug=debug)
        the_flow.run(engine, specs)
    elif RE_PTLF_ZIP.match(path.name): 
        the_flow = flow.DayDataFlow.from_zipfile(path, debug=debug)
        the_flow.run(engine, specs)
    else:
        raise ValueError(f"Path {path.name} doesnt conform to PTLF path forms.")


def _multi_run(path:Path, specs:dict, engine:alq.Engine, debug:bool): 
    zip_dir = path.with_suffix('') 
    with zipfile.ZipFile(path) as z: 
        z.extractall(path=zip_dir)
    for ff in zip_dir.iterdir(): 
        _single_run(ff, specs, engine, debug)


def from_path(path:Path, *, debug:bool=False):
    cfg = config.Settings()
    eng_args = ({} if not debug else 
        dict(fast_executemany=False, echo='debug'))
    alq_eng = engine.get_engine(cfg, **eng_args)
    specs = typer.read_specs() 
    
    mm_zip = RE_PTLF_ZIP.match(path.name)
    if zipfile.is_zipfile(str(path)) and not mm_zip:
        _multi_run(path, specs, alq_eng, debug)
    else: 
        _single_run(path, specs, alq_eng, debug)
