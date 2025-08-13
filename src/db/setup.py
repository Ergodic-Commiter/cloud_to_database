from operator import methodcaller as σ
import sqlalchemy as alq

from src.db import engine as db_eng, typer


def create_ptlf():
    """Crea la tabla PTLF"""
    
    alq_engine = db_eng.get_engine()
    alq_metadata = alq.MetaData()
    
    ptlf_df = db_eng.read_specs()
    ptlf_attrs = map(typer.TypeManager.from_specs, ptlf_df.itertuples())
    ptlf_cols = map(σ('alq_mssql'), ptlf_attrs)
    ptlf_tbl = alq.Table('PTLF', alq_metadata, *ptlf_cols)
    
    sql_str = str(alq.schema
        .CreateTable(ptlf_tbl)
        .compile(dialect=alq_engine.dialect))
    with open("refs/ptlf_create.sql", 'w', encoding='utf-8') as f: 
        f.write(sql_str)    
    alq_metadata.create_all(alq_engine)


if __name__ == '__main__':     
    create_ptlf()
