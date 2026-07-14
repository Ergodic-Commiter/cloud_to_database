# Propuesto por ChatGPT, pero no me encanta este script. 

import sqlalchemy as alq
from sqlalchemy import engine as eng, exc

from ptlf.core import errors as ee


def _get_table(engine:eng.Engine, table=None):
    table = table or 'PTLF_track' 
    alq_meta = alq.MetaData()
    try: 
        return alq.Table(table, alq_meta, autoload_with=engine)
    except exc.ProgrammingError as exx:
        raise ee.PTLFConnError(table) from exx


def start_raw(engine:eng.Engine, file_meta) -> int:
    t_track = _get_table(engine)
    insert_values = file_meta | dict(raw_status='running', raw_start=alq.func.sysutcdatetime())
    insert_stmt = (alq.insert(t_track).values(**insert_values)
        .returning(t_track.c.track_id))
    with engine.begin() as conn:
        track_id = conn.execute(insert_stmt).scalar_one()
    return int(track_id)


def finish_raw(engine:eng.Engine, track_id:int, raw_status:str) -> None:
    t_track = _get_table(engine)
    update_stmt = (alq.update(t_track)
        .where(t_track.c.track_id == track_id)
        .values(raw_finish = alq.func.sysutcdatetime(), 
                raw_status = raw_status))
    with engine.begin() as conn: 
        conn.execute(update_stmt)
    return


def delete_raw(engine:eng.Engine, a_date:str) -> None: 
    t_trk = _get_table(engine)
    t_raw = _get_table(engine, 'PTLF_raw')
    one_raw = (alq.delete(t_raw)
        .where(t_raw.c["NGBBSE24-AUTH-POST-DAT"] == a_date))
    two_trk = (alq.delete(t_trk)
        .where(t_trk.c['data_date'] == a_date))
    with engine.begin() as conn: 
        conn.execute(one_raw)
        conn.execute(two_trk)
    return

