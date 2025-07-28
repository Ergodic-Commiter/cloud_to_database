from operator import methodcaller as σ
from warnings import warn
import sqlalchemy as alq

from src import config as cfg, tools
from . import engine as db_engine


def create_ptlf(rm_desc=False): 
    alq_engine = db_engine.get_engine()
    alq_metadata = alq.MetaData()

    if rm_desc: 
        warn("Removing descriptions on PTLF table.")

    λ_mutate = dict(
        Name0 = lambda df: df['Field Name'].str.strip().str.replace(' ', ''), 
        Name1 = lambda df: db_engine.index_duplicates(df['Name0']))
    
    ptlf_ref = ('data/PTLF-cols.xlsx', 'LO', 'ptlf_cols')
    ptlf_df = tools.read_excel_table(*ptlf_ref).assign(**λ_mutate)
    ptlf_cols = [db_engine.row_to_colspec(rr, not rm_desc) for rr in ptlf_df.itertuples()]
    ptlf_tbl = alq.Table('PTLF', alq_metadata, *ptlf_cols)
    
    # Write to file and create in database. 
    sql_str = str(alq.schema.CreateTable(ptlf_tbl)
        .compile(dialect=alq_engine.dialect))
    with open("refs/ptlf_create.sql", 'w', encoding='utf-8') as _f: 
        _f.write(sql_str)    
    alq_metadata.create_all(alq_engine)


if __name__ == '__main__':     
    create_ptlf()
