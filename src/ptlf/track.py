from __future__ import annotations

import sqlalchemy as alq
from sqlalchemy import engine as eng, exc

from src.ptlf import errors as ee


def get_table(engine): 
    alq_meta = alq.MetaData()
    try: 
        return alq.Table('PTLF_track', alq_meta, autoload_with=engine)
    except exc.ProgrammingError as exx:
        raise ee.PTLFConnError('tabla-PTLF') from exx


def start_raw(engine:eng.Engine, file_meta) -> int:
    t_track = get_table(engine)
    insert_values = file_meta | dict(raw_status='running', raw_start=alq.func.sysutcdatetime())
    insert_stmt = (alq.insert(t_track).values(**insert_values)
        .returning(t_track.c.track_id))
    with engine.begin() as conn:
        track_id = conn.execute(insert_stmt).scalar_one()
    return int(track_id)


def finish_raw(engine:eng.Engine, track_id:int, raw_status:str) -> None:
    t_track = get_table(engine)
    update_stmt = (alq.update(t_track)
        .where(t_track.c.track_id == track_id)
        .values(raw_finish = alq.func.sysutcdatetime(), 
                raw_status = raw_status))
    with engine.begin() as conn: 
        conn.execute(update_stmt)
    return

def delete_raw(engine:eng.Engine, data_date:str): 
    t_track = get_table(engine)
    del_stmt = (alq.delete(t_track)
        .where(t_track.c.data_date == data_date))
    with engine.begin() as conn: 
        conn.execute(del_stmt)
    return

