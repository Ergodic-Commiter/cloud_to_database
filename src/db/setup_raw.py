from operator import methodcaller as σ
import sqlalchemy as alq

from src.db import engine, typer, data
# pylint:disable=invalid-name


if __name__ == '__main__':    

    ptlf_df = data.read_specs()
    ptlf_attrs = map(typer.TypeManager.from_specs, ptlf_df.itertuples())
    ptlf_cols = list(map(σ('alq_mssql'), ptlf_attrs))
    
    alq_engine = engine.get_engine()
    alq_metadata = alq.MetaData()
    ptlf_tbl = alq.Table('PTLF_raw', alq_metadata, *ptlf_cols)
    
    sql_str = str(alq.schema
        .CreateTable(ptlf_tbl)
        .compile(dialect=alq_engine.dialect))

    with open("refs/ptlf_create.sql", 'w', encoding='utf-8') as f: 
        f.write(sql_str)    
    alq_metadata.create_all(alq_engine)

