from datetime import datetime as dt, timedelta as delta
import hashlib
import os
from pathlib import Path
import re
from typing import Optional

import pandas as pd
from .misc import noner
# pylint: disable=invalid-name


def index_duplicates(srs:pd.Series):
    """Si en la serie hay repetidos, los numeramos para que no haya."""
    occurrence = srs.groupby(srs).cumcount() + 1
    duplicates = srs.duplicated(False)
    suffix = ('_' + occurrence.astype(str)).where(duplicates, '')
    return srs+suffix


def _sha256_file(path:str, chunk=1024*1024) -> bytes:  # 10**20. 
    """Se usa para asegurar que los archivos no se cargan duplicados en SQL."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.digest()


def file_meta(path:Path|str) -> dict:
    """Función asociada a la SQL-tabla PTLF-track."""
    path = Path(path)
    with open(path, encoding='latin1') as ff: 
        n_records = sum(1 for _ in ff)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
    if not date_match: 
        raise ValueError(f"Path named {path.name} doesnt match date format 'YYYY-MM-DD'")
    date_file = dt.strptime(date_match.group(0), '%Y-%m-%d').date()
    data_date = date_file.strftime('%y%m%d')
    meta = dict(
        file_name = path.name,
        file_path = noner(os.fspath)(path),
        file_size = path.stat().st_size,
        file_hash = _sha256_file(path),
        n_records = n_records, 
        date_file = date_file, 
        data_date = data_date)
    return meta


### Ya no se usan: 

 
def prev_datestr(datestr, dt_format='%y%m%d'): 
    a_date = dt.strptime(datestr, dt_format)
    p_date = a_date + delta(days=-1)
    return p_date.strftime(dt_format)


def check_file_rows(file, mode='all-equal', **kwargs):
    """Revisar la longitud de las filas de los archivos fixed-widths: 
    {all-equal, less-than}"""
    with open(file, 'r', encoding='latin1') as f:
        lengths = list(map(len, f))
    if mode == 'all-equal': 
        l0 = lengths[0]
        assert all(ll == l0 for ll in lengths),\
            f"Lines in '{file}' have different lengths."
        return l0
    if mode == 'less-than': 
        max_l = max(lengths)
        sum_len = kwargs['sum_length']
        assert max_l <= sum_len,\
            f"There are lines longer ({max_l}) than the specified length {sum_len}"
        return max_l
    err_msg = f"Check rows mode {mode} can only be one of [all_equal, less_than]"
    raise ValueError(err_msg)


def trim_file(a_file, length):
    """Hubieron algunos fixed-widths con filas más largas que lo supuestos.""" 
    a_file = Path(a_file)
    trim_2 = a_file.parents[1]/'trim'/a_file.name
    λ_trim = lambda ll: ll[:length]+b'\n'
    with open(a_file, 'rb') as r, open(trim_2, 'wb') as w: 
        for line in r: 
            w.write(λ_trim(line))
    return str(trim_2)



def files_to_dataframe(data_dir:Optional[Path]=None): 
    data_dir = data_dir or Path('data/temp')
    ptlf_gen = map(file_meta, data_dir.rglob("PTLF_[0-9-]*"))
    dir_status = {'text' : 'incierto', 
        'failed/3-start' : 'pos.repetido',
        'failed/4-upload': 'err.carga'}
    mutates = dict(
        data_date = pd.NaT, 
        n_meta = lambda df: df['n_records'], 
        n_data = pd.NA, 
        estatus = lambda df: df['file_path'].str
            .extract(rf"{data_dir}/(.*)/PTLF").replace(dir_status))
    χ_extension = lambda df: ~df['file_name'].str.endswith('.txt', na=False)
    keep_cols = ['file_name', 'data_date', 'n_meta', 'n_data', 'estatus']
    ptlf_df = (pd.DataFrame.from_records(ptlf_gen)
        .assign(**mutates)
        .loc[χ_extension, keep_cols])
    ptlf_df.to_clipboard(index=False, header=False, excel=True)
    return ptlf_df