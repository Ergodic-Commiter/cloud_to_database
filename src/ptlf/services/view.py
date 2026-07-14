from operator import attrgetter as ɑ
from pathlib import Path
from warnings import warn

# pylint: disable=no-name-in-module
from ibis import backends, cases, _
import pandas as pd
import sqlalchemy as alq
from toolz import functoolz as fz

from ptlf import engine as eng, render as rr, settings as ss
from ptlf.core import errors as ee, specs as spx
# pylint: disable=unused-argument
  

def create_user(name, password): 
    # CREATE USER [prevencion.fraudes] WITH PASSWORD = 'Untold-Litigate-Culminate';
    # ALTER ROLE r_ops ADD MEMBER [prevencion.fraudes]; 
    # GRANT SELECT ON dbo.v_PTLF_Fraudes TO r_ops;    
    pass 


def create_view(user_col, to_file:Path=None): 
    cfg = ss.config
    to_file = to_file or cfg.refs_dir/f"users/{user_col}_view.sql"
    print(f"Query at: {to_file}")
    ptlf_specs = spx.read_specs()

    if user_col not in ptlf_specs.columns:
        raise ee.SpecsPTLF_Error(user_col)

    meta = alq.MetaData()
    alq_eng = eng.get_engine(cfg)
    ptlf_tbl = alq.Table('PTLF_raw', meta, schema='dbo', autoload_with=alq_eng)
    def λ_sqlcol(row): 
        name, label = ɑ('Name1', user_col)(row)
        return ptlf_tbl.c[name].label(label)

    new_specs = ptlf_specs[~ptlf_specs[user_col].isnull()]
    alq_stmt = alq.select(*map(λ_sqlcol, new_specs.itertuples()))
    sql_stmt = (alq_stmt.compile(alq_eng, compile_kwargs=dict(literal_binds=True))
        .string.replace(', dbo', ',\n\tdbo'))
    Path(to_file).write_text(sql_stmt, encoding='utf8')


def create_pqms(user_col, to_dir:Path=None):
    to_dir = to_dir or ss.config.refs_dir/'powerquery'
    u_key = user_col.replace('Alias', '')
    
    u_df = (spx.read_specs()
        .assign(new_name = lambda df: df[user_col].str.replace('*', ''), 
            is_key = lambda df: df[user_col].str.contains('*', regex=False, na=False))
        .query("is_key"))
    spec_2_pqm = fz.compose_left(
        spx.FieldSpec.model_validate, 
        spx.PqmTemplate)
    u_pqms = [spec_2_pqm(spec) 
        for spec in u_df.to_dict('records')]
    renderers = [
        rr.Renderer.create('exacto', f'v_PTLF_{u_key}', u_pqms),
        rr.Renderer.create('explora', u_pqms)]
    for renderer in renderers: 
        renderer.write(to_dir/f"_PTLF_{u_key}_{renderer.key.title()}.pqm")
    

def check_status(query: str|int = None) -> pd.DataFrame:
    query = query or 15
    conn = eng.get_connection(conn_type='ibis')
    match query: 
        case int() as kk:
            post_check = False
            stmt = _ptlf_stmt(conn)
        case str() as qq:
            (kk, post_check) = (100, True)
            stmt = (_ptlf_stmt(conn).alias('ptlf')
                .sql(f"select * from ptlf where {qq}"))
    df = (stmt
        .order_by(_['file_name'].desc()).limit(kk)
        .to_pandas()
        .assign(n_data = lambda df_: df_['n_data'].astype('Int64')))
    if post_check and len(df) == kk: 
        warn(f"String query result has limit ({kk}), possibly truncated result.")
    return df



def _ptlf_stmt(conn:backends.BaseBackend):
    track = conn.table('PTLF_track')
    status_q = (conn.table('PTLF_raw')
        .group_by(date_str = _['NGBBSE24-AUTH-POST-DAT'])
        .aggregate(n_data = _.count().cast('Int64'))
        .right_join(track, _.date_str == track.data_date)
        .mutate(data_date = _['data_date'].cast('date'),  
            n_meta = _['n_records'], 
            estatus = cases(
            (_.n_data.isnull(), 'en ejecucion'), 
            (_.n_data == _.n_records, 'cargado'), 
            (_.n_data < _.n_records, 'incompleto')))
        .select('file_name', 'data_date', 'n_meta', 'n_data', 'estatus'))
    return status_q


def _write_query(): 
    pass


def _upload_view():
    pass

