from __future__ import annotations
import os, socket, hashlib
from datetime import date
from typing import Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine
# pylint: disable=too-many-arguments


# ---------- file metadata helpers ----------
def sha256_file(path:str, chunk=1024*1024) -> bytes:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.digest()

def file_meta(path:str) -> dict:
    meta_dict = dict(
        file_name = os.path.basename(path),
        file_path = os.path.abspath(path),
        file_size_bytes = os.path.getsize(path),
        file_hash_sha256 = sha256_file(path))
    return meta_dict


# ---------- PTLF_track lifecycle helpers ----------
def track_start_raw(engine:Engine, *,
        file_name:str, file_path:Optional[str]=None, 
        file_size_bytes:Optional[int]=None, file_hash_sha256:Optional[bytes]=None, 
        date_str:Optional[str]=None, date_file:Optional[date]=None,
        run_by:Optional[str]=None, run_host:Optional[str]=None
        ) -> int:
    """
    Insert a row marking RAW phase start. Returns track_id.
    Timestamps come from SQL Server using SYSUTCDATETIME().
    """
    run_by = run_by or os.getenv("USER") or os.getenv("USERNAME")
    run_host = run_host or socket.gethostname()

    sql = text("""
    INSERT INTO dbo.PTLF_track
      (file_name, file_path, file_size_bytes, file_hash_sha256,
       date_str, date_file, raw_start, raw_status, run_by, run_host)
    OUTPUT inserted.track_id
    VALUES
      (:file_name, :file_path, :file_size_bytes, :file_hash_sha256,
       :date_str, :date_file, SYSUTCDATETIME(), 'running', :run_by, :run_host);
    """)
    params = dict(file_name=file_name, file_path=file_path,
        file_size_bytes=file_size_bytes, file_hash_sha256=file_hash_sha256,
        date_str=date_str, date_file=date_file,
        run_by=run_by, run_host=run_host)
    with engine.begin() as conn:
        track_id = conn.execute(sql, params).scalar_one()
    return int(track_id)


def track_complete_raw(engine:Engine, *,
        track_id:int, n_records:Optional[int]=None, 
        error:Optional[str]=None
        ) -> None:
    sql = text("""
    UPDATE dbo.PTLF_track
       SET raw_complete = SYSUTCDATETIME(),
           raw_status   = CASE WHEN :error IS NULL THEN 'success' ELSE 'failed' END,
           n_records    = :n_records,
           raw_error    = :error
     WHERE track_id = :track_id;
    """)
    with engine.begin() as conn:
        conn.execute(sql, dict(track_id=track_id, n_records=n_records, error=error))
    return


def track_start_ops(engine:Engine, *, track_id: int) -> None:
    sql = text("""
    UPDATE dbo.PTLF_track
       SET ops_start = SYSUTCDATETIME(),
           ops_status = 'running'
     WHERE track_id = :track_id;
    """)
    with engine.begin() as conn:
        conn.execute(sql, {"track_id": track_id})
    return


def track_complete_ops(engine:Engine, *, track_id:int,
        inserted_rows:Optional[int]=None, updated_rows:Optional[int]=None,
        rejected_rows:Optional[int]=None, error:Optional[str]=None
        ) -> None:
    sql = text("""
    UPDATE dbo.PTLF_track
       SET ops_complete  = SYSUTCDATETIME(),
           ops_status    = CASE WHEN :error IS NULL THEN 'success' ELSE 'failed' END,
           inserted_rows = :inserted_rows,
           updated_rows  = :updated_rows,
           rejected_rows = :rejected_rows,
           ops_error     = :error
     WHERE track_id = :track_id;
    """)
    with engine.begin() as conn:
        conn_dict = dict(track_id=track_id, 
            inserted_rows=inserted_rows, updated_rows=updated_rows, 
            rejected_rows=rejected_rows, error=error)
        conn.execute(sql, conn_dict)
    return


# ---------- convenience wrappers ----------
def track_start_raw_from_path(engine:Engine, *,
        path:str, date_str:Optional[str]=None, date_file:Optional[date]=None,
        run_by:Optional[str]=None, run_host:Optional[str]=None
        ) -> int:
    meta = file_meta(path)
    start_args = dict(file_name=meta["file_name"], file_path=meta["file_path"],
        file_size_bytes=meta["file_size_bytes"], file_hash_sha256=meta["file_hash_sha256"],
        date_str=date_str, date_file=date_file,
        run_by=run_by, run_host=run_host)
    return track_start_raw(engine, **start_args)
