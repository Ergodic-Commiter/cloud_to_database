from datetime import datetime as dt
import os 
from pathlib import Path
import re
import zipfile

import sqlalchemy as alq
from ptlf import engine as ptlf_eng, flow
from ptlf.core import settings, models


RE_PTLF_DAT = re.compile(r"^PTLF_([\d\-]{10})$")
RE_PTLF_ZIP = re.compile(r"^PRD_TRXS_PTLF_([\d\-]{10}).ZIP$")

def upload_data(path:Path, *, debug:bool=False):
    cfg = settings.Settings()
    eng_args = ({} if not debug else 
        dict(fast_executemany=False, echo='debug'))
    alq_eng = ptlf_eng.get_engine(cfg, **eng_args)
    specs = models.read_specs() 
    mm_zip = RE_PTLF_ZIP.match(path.name)
    if zipfile.is_zipfile(os.fspath(path)) and not mm_zip:
        _zip_run(path, specs, alq_eng, debug)
    else: 
        _single_run(path, specs, alq_eng, debug)

def reload_data(path:Path, *, debug:bool=False): 
    cfg = settings.Settings()
    specs = models.read_specs() 
    eng_args = ({} if not debug else 
        dict(fast_executemany=False, echo='debug'))
    alq_eng = ptlf_eng.get_engine(cfg, **eng_args)
    the_flow = flow.DayDataFlow.from_data(path, debug=debug)
    the_flow.delete_from(alq_eng)
    the_flow.run(alq_eng, specs)

def delete_date(date:dt.date, *, debug:bool=False): 
    cfg = settings.Settings()
    eng_args = ({} if not debug else 
        dict(fast_executemany=False, echo='debug'))
    alq_eng = ptlf_eng.get_engine(cfg, **eng_args)
    the_flow = flow.DayDataFlow.from_date(date, cfg.data_loc, debug=debug)
    the_flow.delete_from(alq_eng)


def _single_run(path:Path, specs:dict, engine:alq.Engine, debug:bool): 
    if RE_PTLF_DAT.match(path.name): 
        the_flow = flow.DayDataFlow.from_data(path, debug=debug)
        the_flow.run(engine, specs)
    elif RE_PTLF_ZIP.match(path.name): 
        the_flow = flow.DayDataFlow.from_zipfile(path, debug=debug)
        the_flow.run(engine, specs)
    else:
        raise ValueError(f"Path {path.name} doesnt conform to PTLF path forms.")


def _zip_run(path:Path, specs:dict, engine:alq.Engine, debug:bool): 
    zip_dir = path.with_suffix('') 
    with zipfile.ZipFile(path) as z: 
        z.extractall(path=zip_dir)
    for ff in zip_dir.iterdir(): 
        _single_run(ff, specs, engine, debug)

