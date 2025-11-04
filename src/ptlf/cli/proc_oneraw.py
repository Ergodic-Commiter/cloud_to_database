from datetime import date, datetime as dt
import logging
from sys import argv

from ptlf import core, infra, services
# pylint: disable=invalid-name



if __name__ == '__main__':
    date_str = argv[1] if len(argv) > 1 else None
    debug = (len(argv) > 2) and (argv[2] == 'debug')
    the_date = dt.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    cfg = core.Settings()
    infra.logging.setup(cfg)
    logger = logging.getLogger('ptlf.log')
    
    config = services.FlowConfig(the_date, cfg.data_loc, debug=debug)    
    the_flow = services.DayDataFlow(config)    
    
    eng_args = dict(fast_executemany=False, echo='debug') if debug else {}
    alq_eng = core.get_engine(cfg, **eng_args)
    container = infra.get_container(cfg)
    
    at_stage = the_flow.determine_stage(alq_eng, container)
    if at_stage == 3:
        print("Downloading from Azure Storage..." )
        the_flow.download_cloud(container)
    if at_stage >= 2: 
        print("Extracting zipfile...")
        the_flow.extract_zipfile()
    if at_stage >= 1: 
        print("Reading data and uploading ...")
        the_flow.run(alq_eng)
    
    
        
    