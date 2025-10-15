from operator import methodcaller as σ
import sqlalchemy as alq

from ptlf import engine, typer
from ptlf.config import Settings
# pylint: disable=invalid-name

if __name__ == '__main__':    

    ptlf_df = typer.read_specs()
    ptlf_attrs = map(typer.Typer.from_specs, ptlf_df.itertuples())
    ptlf_cols = list(map(σ('alq_mssql'), ptlf_attrs))
    
    cfg = Settings()
    alq_engine = engine.get_engine(cfg)
    alq_metadata = alq.MetaData()
    ptlf_tbl = alq.Table('PTLF_raw', alq_metadata, *ptlf_cols)
    
    sql_str = str(alq.schema
        .CreateTable(ptlf_tbl)
        .compile(dialect=alq_engine.dialect))

    with open("refs/ptlf_create.sql", 'w', encoding='utf-8') as f: 
        f.write(sql_str)    
    alq_metadata.create_all(alq_engine)

