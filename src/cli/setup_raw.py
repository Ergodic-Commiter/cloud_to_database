import sqlalchemy as alq

from ptlf import engine, settings as ss
from ptlf.core import specs as spx
# pylint: disable=invalid-name


if __name__ == '__main__':    
    ptlf_df = spx.read_specs()
    ptlf_specs = spx.FieldSpec.dataframe_dict(ptlf_df)
    ptlf_cols = [spx.MssqlUpload(spec).alq_column() 
        for spec in ptlf_specs.values()]
    # from_specs = models.Converter.from_specs
    # [ from_specs(spec_tpl).alq_mssql for spec_tpl in ptlf_df.itertuples() ]
    
    alq_eng = engine.get_engine(ss.config)
    alq_meta = alq.MetaData()
    ptlf_tbl = alq.Table('PTLF_raw', alq_meta, *ptlf_cols)
    
    sql_str = str(alq.schema
        .CreateTable(ptlf_tbl)
        .compile(dialect=alq_eng.dialect))

    with open("refs/sql/ptlf_create_2.sql", 'w', encoding='utf-8') as f: 
        f.write(sql_str)    
    # alq_meta.create_all(alq_eng)

