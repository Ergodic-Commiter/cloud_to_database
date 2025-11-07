# pylint: disable=not-callable
# pylint: disable=no-name-in-module
from operator import attrgetter as ɑ
from pathlib import Path

from ibis import _, backends, cases
import pandas as pd
import sqlalchemy as alq
from ptlf.core import engine as eng, errors as ee, models, settings

cfg = settings.Settings()

def _write_query(): 
    pass

def _upload_view():
    pass


def create_view(from_col): 
    to_file = Path(f'refs/users/{from_col}_view.sql')
    print(f"Query at: {to_file}")

    ptlf_specs = models.read_specs(output='dataframe')
    if from_col not in ptlf_specs.columns: ## Se cambió PTLF_SPECS de data_frame a diccionario.  
        raise ee.SpecsPTLF_Error(from_col)

    meta = alq.MetaData()
    alq_eng = eng.get_engine(cfg)
    ptlf_tbl = alq.Table('PTLF_raw', meta, schema='dbo', autoload_with=alq_eng)
    def λ_sqlcol(row): 
        name, label = ɑ('Name1', from_col)(row)
        return ptlf_tbl.c[name].label(label)

    new_specs = ptlf_specs[~ptlf_specs[from_col].isnull()]
    alq_stmt = alq.select(*map(λ_sqlcol, new_specs.itertuples()))
    sql_stmt = (alq_stmt.compile(alq_eng, compile_kwargs=dict(literal_binds=True))
        .string.replace(', dbo', ',\n\tdbo'))
    Path(to_file).write_text(sql_stmt, encoding='utf8')


def _alchemy_subquery(engine:alq.Engine):
    # Deprecado, mucho mejor con IBIS. 
    meta = alq.MetaData() 
    trk = alq.Table('PTLF_track', meta, autoload_with=engine)
    raw = alq.Table('PTLF_raw', meta, autoload_with=engine)
    raw_g = (alq.select(
            (date_str := raw.c['NGBBSE24-AUTH-POST-DAT']).label('date_str'), 
            alq.func.count().label('n_data'))
        .group_by(date_str)
        .subquery('raw_g'))
    estatus = (alq.case(
        (raw_g.c['n_data'].is_(None), 'en ejecucion'), 
        (raw_g.c['n_data'] == trk.c['n_records'], 'cargado'), 
        (raw_g.c['n_data'] < trk.c['n_records'], 'incompleto'))
        .label('estatus'))
    convert_args = (alq.literal_column('DATE'), trk.c['data_date'], alq.literal(12))
    status_q = (alq.select(
            trk.c['file_name'], 
            alq.func.CONVERT(*convert_args).label('data_date'), 
            trk.c['n_records'].label('n_meta'), 
            raw_g.c['n_data'], 
            estatus)
        .select_from(trk.outerjoin(raw_g, 
            trk.c['data_date'] == raw_g.c['date_str']))
        .subquery('status'))
    return status_q 

def _ibis_subquery(conn:backends.BaseBackend):
    track = conn.table('PTLF_track')
    status_q = (conn.table('PTLF_raw')
        .group_by(date_str = _['NGBBSE24-AUTH-POST-DAT'])
        .aggregate(n_data = _.count())
        .left_join(track, _.date_str == track.data_date)
        .mutate(n_meta = _['n_records'], 
            estatus = cases(
            (_.n_data.isnull(), 'en ejecucion'), 
            (_.n_data == _.n_records, 'cargado'), 
            (_.n_data < _.n_records, 'incompleto')))
        .select('file_name', 'data_date', 'n_meta', 'n_data', 'estatus'))
    return status_q

def check_status(eng_type:str='ibis'):
    if eng_type == 'ibis': 
        conn = eng.get_connection(conn_type='ibis')
        status_df = (_ibis_subquery(conn)
            .order_by(_['file_name'].desc())
            .limit(15))
        return status_df.to_pandas()
    if eng_type == 'sqlalchemy': 
        alq_eng = eng.get_engine(cfg)
        pre_query = _alchemy_subquery(alq_eng)
        query = (alq.select(pre_query)
            .order_by(pre_query.c['file_name'].desc())
            .limit(15))
        return pd.read_sql(query, alq_eng) 
    raise ValueError("Engine (type) must be [ibis, sqlalchemy]")