from operator import methodcaller as σ
import sqlalchemy as alq

from ptlf import core
from ptlf.core import models
# pylint: disable=invalid-name

from_specs 

if __name__ == '__main__':    
    ptlf_df = models.read_specs()
    ptlf_attrs = map(models.Converter.from_specs, ptlf_df.itertuples())
    ptlf_cols = list(map(σ('alq_mssql'), ptlf_attrs))
    # from_specs = models.Converter.from_specs
    # [ from_specs(spec_tpl).alq_mssql for spec_tpl in ptlf_df.itertuples() ]
    
    cfg = core.Settings()
    alq_eng = core.get_engine(cfg)
    alq_meta = alq.MetaData()
    ptlf_tbl = alq.Table('PTLF_raw', alq_meta, *ptlf_cols)
    
    sql_str = str(alq.schema
        .CreateTable(ptlf_tbl)
        .compile(dialect=alq_eng.dialect))

    with open("refs/ptlf_create.sql", 'w', encoding='utf-8') as f: 
        f.write(sql_str)    
    alq_meta.create_all(alq_eng)

