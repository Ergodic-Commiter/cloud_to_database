from operator import methodcaller as σ
import sqlalchemy as alq
from sqlalchemy import orm, schema 
from toolz import curried as cz

from ..tools import read_excel_table, partial2, star, thread
from .. import config as cfg
from .. import db
from . import run


def main(): 
    # Get the columns, index duplicate names, and into a table. 
    λ_mutate = dict(
        Name0 = lambda df: df['Field Name'].str.strip().str.replace(' ', ''), 
        Name1 = lambda df: run.index_duplicates(df['Name0']))
    
    ptlf_ref = ('data/PTLF-cols.xlsx', 'LO', 'ptlf_cols')
    ptlf_df = run.read_excel_table(*ptlf_ref).assign(**λ_mutate)
    ptlf_cols = [run.row_to_colspec(rr) for rr in ptlf_df.itertuples()]
    ptlf_tbl = alq.Table('PTLF', db.metadata, *ptlf_cols)
    
    # ptlf_tbl = thread(('data/PTLF-cols.xlsx', 'LO', 'ptlf_cols'), 
    #     star(run.read_excel_table), 
    #     partial2(σ('assign'), **λ_mutate), 
    #     σ('itertuples'), 
    #     cz.map(run.row_to_colspec), 
    #     star(partial2(alq.Table, 'PTLF', db.metadata, ...)))
    
    # Write to file and create in database. 
    sql_str = str(schema.CreateTable(ptlf_tbl)
        .compile(dialect=db.engine.dialect))
    with open("refs/ptlf_create.sql", 'w', encoding='utf-8') as f: 
        f.write(sql_str)    
    db.metadata.create_all(db.engine)


if __name__ == '__main__':     
    main()
