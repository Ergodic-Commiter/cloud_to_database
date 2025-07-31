import sqlalchemy as alq
from src.db import engine as db_eng

MAX_PARAMS = 2100

def error_lengths(data, specs):     
    err_cols = []
    for name, len_exp in zip(specs.Name1, specs.Length):
        if name not in data.columns: 
            print(f"\t{name} not found in Data.")
            continue

        
        max_len = data[name].astype(str).str.len().max()
        if max_len > len_exp:
            err_cols.append(name)
            print(f"{name} overflows: {max_len} > {len_exp}")
    return err_cols


if __name__ == '__main__':     
    file_name = 'data/PTLF_2024-12-30.txt'
    ptlf_df0 = db_eng.read_ptlf(file_name, read_via='io')
    ptlf_df1 = db_eng.clean_binaries(ptlf_df0)
    max_rows = MAX_PARAMS // ptlf_df1.shape[1]
    
    alq_eng = db_eng.get_engine(fast_exec=True)
    sql_params = dict(name="PTLF", con=alq_eng, schema='dbo', 
        #if_exists='append', index=False)
        if_exists='append', index=False, method='multi', chunksize=max_rows)
    ptlf_df1.to_sql(**sql_params)
    

