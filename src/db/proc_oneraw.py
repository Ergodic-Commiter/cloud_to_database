from datetime import date, datetime as dt
from pathlib import Path
from sys import argv

from src.db import flow, engine
from src import config as cfg, storage as stg
# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name



if __name__ == '__main__':
    date_str = argv[1] if len(argv) > 1 else None
    debug = (len(argv) > 2) and (argv[2] == 'debug')
    the_date = dt.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    workdir = Path(cfg.DATA_LOC)
    
    config = flow.FlowConfig(the_date, workdir)    
    the_flow = flow.DayDataFlow(config)    
    
    eng_args = dict(fast_executemany=False, echo='debug') if debug else {}
    alq_eng = engine.get_engine(**eng_args)
    container = stg.engine.get_container()
    
    at_stage = the_flow.determine_stage(alq_eng, container)
    if at_stage == 3:
        print("Downloading from Azure Storage..." )
        the_flow.download_cloud(container)
    if at_stage >= 2: 
        print("Extracting zipfile...")
        the_flow.extract_zipfile()
    if at_stage >= 1: 
        print("Reading data and uploading ...")
        the_flow.run(alq_eng, debug=debug)
    
    
        
    