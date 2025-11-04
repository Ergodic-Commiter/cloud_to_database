from operator import attrgetter as ɑ
from pathlib import Path

import pandas as pd
import sqlalchemy as alq
from ptlf import core
from ptlf.core import errors as ee, models
# pylint: disable=not-callable

cfg = core.Settings()

def _write_query(): 
    pass

def _uplaod_view():
    pass


def create_view(from_col): 
    to_file = Path(f'refs/users/{from_col}_view.sql')
    print(f"Query at: {to_file}")

    ptlf_specs = models.read_specs(output='dataframe')
    if from_col not in ptlf_specs.columns: ## Se cambió PTLF_SPECS de data_frame a diccionario.  
        raise ee.SpecsPTLF_Error(from_col)

    meta = alq.MetaData()
    alq_eng = core.get_engine(cfg)
    ptlf_tbl = alq.Table('PTLF_raw', meta, schema='dbo', autoload_with=alq_eng)
    def λ_sqlcol(row): 
        name, label = ɑ('Name1', from_col)(row)
        return ptlf_tbl.c[name].label(label)

    new_specs = ptlf_specs[~ptlf_specs[from_col].isnull()]
    alq_stmt = alq.select(*map(λ_sqlcol, new_specs.itertuples()))
    sql_stmt = (alq_stmt.compile(alq_eng, compile_kwargs=dict(literal_binds=True))
        .string.replace(', dbo', ',\n\tdbo'))
    Path(to_file).write_text(sql_stmt, encoding='utf8')

    
def _prepare_query(engine=alq.Engine): 
    meta = alq.MetaData() 
    trk = alq.Table('PTLF_track', meta, autoload_with=engine)
    raw = alq.Table('PTLF_raw', meta, autoload_with=engine)
    raw_g = alq.select(
            (date_str := raw.c['NGBBSE24-AUTH-POST-DAT']).label('date_str'), 
            alq.func.count().label('n_data')
        ).group_by(date_str
        ).subquery('raw_g')
    estatus = alq.case(
            (raw_g.c['n_data'].is_(None), 'en ejecucion'), 
            (raw_g.c['n_data'] == trk.c['n_records'], 'cargado'), 
            (raw_g.c['n_data'] < trk.c['n_records'], 'incompleto')
        ).label('estatus')
    convert_args = (alq.literal_column('DATE'), trk.c['data_date'], alq.literal(12))
    query = alq.select(
            trk.c['file_name'], 
            alq.func.CONVERT(*convert_args).label('data_date'), 
            trk.c['n_records'].label('n_meta'), 
            raw_g.c['n_data'], 
            estatus
        ).select_from(trk.outerjoin(raw_g, 
            trk.c['data_date'] == raw_g.c['date_str'])
        ).subquery('status')
    return query
    # SELECT t.file_name, 
    #   CONVERT(DATE, t.data_date,12) as data_date, 
    #   t.n_records as n_meta, r.n_data, 
    #   case when r.n_data = t.n_records then 'cargado' 
    #       when r.n_data is NULL then 'en ejecucion'
    #       when r.n_data < t.n_records then 'incompleto'
    #   end as estatus
    # FROM PTLF_track t
    # LEFT JOIN (SELECT
    #     [NGBBSE24-AUTH-POST-DAT] as date_str, 
    #   COUNT(*) as n_data
    #     FROM PTLF_raw 
    #     GROUP BY [NGBBSE24-AUTH-POST-DAT]
    #     ) r
    # ON t.data_date = r.date_str
    # ORDER BY file_name DESC     

def check_status():
    eng = core.get_engine(cfg)
    pre_query = _prepare_query(eng)
    query = (alq.select(pre_query)
        .order_by(pre_query.c['file_name'].desc())
        .limit(15))
    with eng.connect() as conn: 
        status_df = pd.read_sql(query, conn) 
    return status_df
