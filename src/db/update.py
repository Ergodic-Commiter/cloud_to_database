from pathlib import Path
from sys import argv

from src.db import engine as db_eng



if __name__ == '__main__':
    # pylint: disable=invalid-name
    date_str = argv[1] if len(argv) > 1 else '2025-08-06'
    file_name = Path.cwd()/f'data/temp/text/PTLF_{date_str}'
    ptlf_df0 = db_eng.read_ptlf(file_name)
    
    alq_eng = db_eng.get_engine(fast_exec=True)
    sql_params = dict(name="PTLF", con=alq_eng, schema='dbo', 
        if_exists='append', index=False)
    ptlf_df0.to_sql(**sql_params)
    

