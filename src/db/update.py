from pathlib import Path
from sys import argv

from src.db import engine as db_eng



if __name__ == '__main__':
    # pylint: disable=invalid-name
    # pylint:disable=broad-exception-raised 
    date_str = argv[1] if len(argv) > 1 else '2025-08-06'
    debug = (len(argv) > 2) and (argv[2] == 'debug')
        
    file_path = Path.cwd()/f'data/temp/trim/PTLF_{date_str}'
    ptlf_df0 = db_eng.read_ptlf(file_path)    

    if debug: 
        alq_eng = db_eng.get_engine(fast_executemany=False, echo='debug')
        sql_params = dict(name="PTLF_raw", con=alq_eng, schema='dbo', 
            if_exists='append', index=False, method=None, chunksize=1)
    else: 
        alq_eng = db_eng.get_engine()
        sql_params = dict(name="PTLF_raw", con=alq_eng, schema='dbo', 
            if_exists='append', index=False)
    
    try:
        ptlf_df0.to_sql(**sql_params)
    except Exception as ee:
        raise Exception("Insert failed:") from ee
    
