# pylint: disable=not-callable
# pylint: disable=no-name-in-module
from operator import attrgetter as ɑ
from pathlib import Path

from ibis import _, backends, cases
import sqlalchemy as alq

from ptlf.core import engine as eng, errors as ee, models as mm, settings as ss
from ptlf.render import setup_j2


def create_user(name, password): 
    # CREATE USER [prevencion.fraudes] WITH PASSWORD = 'Untold-Litigate-Culminate';
    # ALTER ROLE r_ops   ADD MEMBER [prevencion.fraudes]; 
    # GRANT SELECT ON dbo.v_PTLF_Fraudes TO r_ops;    
    pass 


def create_view(user_col, to_file:Path=None): 
    to_file = to_file or Path(f'refs/users/{user_col}_view.sql')
    print(f"Query at: {to_file}")
    ptlf_specs = mm.read_specs(output='dataframe')
    if user_col not in ptlf_specs.columns:
        raise ee.SpecsPTLF_Error(user_col)

    cfg = ss.Settings()
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


def check_status(query: str|int = None):
    query = query or 15
    conn = eng.get_connection(conn_type='ibis')
    subq = _ptlf_subquery(conn).order_by(_['file_name'].desc())
    λ_ndata = lambda df: df['n_data'].astype('Int64')

    match query: 
        case int() as kk: 
            pre_q = subq.limit(kk).to_pandas()
        case str() as qq: 
            pre_q = subq.limit(100).to_pandas().query(qq)
    return pre_q.assign(n_data = λ_ndata)


def create_pqms(user_col, to_dir:Path=None):
    u_key = user_col.replace('Alias', '')
    to_dir = to_dir or Path('refs/powerquery')
    tmpl_env = setup_j2(trim_blocks=True, lstrip_blocks=True)

    u_specs = (mm.read_specs(output='dataframe')
        .assign(new_name = lambda df: df[user_col].str.replace('*', ''), 
            is_key = lambda df: df[user_col].str.contains('*', regex=False, na=False))
        .query("is_key")) 
            
    u_cols = mm.Converter.dataframe_to_dict(u_specs)
    u_pqms = [spec.pqm_templater(u_key) for spec in u_cols.values()]

    tmpl_1 = tmpl_env.get_template('PTLF_Exacto.j2.pqm')
    user_1 = tmpl_1.render(view=f'v_PTLF_{u_key}', keys=u_pqms)
    file_1 = to_dir/f'_PTLF_{u_key}_Exacto.pqm'
    file_1.write_text(user_1, encoding='utf8')
    
    tmpl_2 = tmpl_env.get_template('PTLF_Explora.j2.pqm')
    user_2 = tmpl_2.render(view=f'v_PTLF_{u_key}', keys=u_pqms)
    file_2 = to_dir/f'_PTLF_{u_key}_Explora.pqm'
    file_2.write_text(user_2, encoding='utf8')




def _ptlf_subquery(conn:backends.BaseBackend):
    track = conn.table('PTLF_track')
    status_q = (conn.table('PTLF_raw')
        .group_by(date_str = _['NGBBSE24-AUTH-POST-DAT'])
        .aggregate(n_data = _.count())
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

