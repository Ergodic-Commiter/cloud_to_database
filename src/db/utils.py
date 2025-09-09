from datetime import datetime as dt, timedelta as delta
import hashlib
from pathlib import Path
import re

import pandas as pd
# pylint: disable=invalid-name
# pylint: disable=consider-using-with


def prev_datestr(datestr, dt_format='%y%m%d'): 
    a_date = dt.strptime(datestr, dt_format)
    p_date = a_date + delta(days=-1)
    return p_date.strftime(dt_format)


class classproperty(property):
    # Python compliqueitor.
    def __get__(self, _, owner):
        return self.fget(owner)


def noner(func): 
    return lambda x: func(x) if x is not None else None


def index_duplicates(srs:pd.Series):
    duplicates = srs.duplicated(False)
    occurrence = srs.groupby(srs).cumcount() + 1
    suffix = ('_' + occurrence.astype(str)).where(duplicates, '')
    return srs+suffix


def trim_file(a_file, length): 
    a_file = Path(a_file)
    trim_2 = a_file.parents[1]/'trim'/a_file.name
    λ_trim = lambda ll: ll[:length]+b'\n'
    with open(a_file, 'rb') as r, open(trim_2, 'wb') as w: 
        for line in r: 
            w.write(λ_trim(line))
    return str(trim_2)

    
def check_file_rows(file, mode='all_equal', **kwargs):
    with open(file, 'r', encoding='latin1') as f:
        lengths = list(map(len, f))
    if mode == 'all_equal': 
        l0 = lengths[0]
        assert all(ll == l0 for ll in lengths),\
            f"Lines in '{file}' have different lengths."
        return l0
    if mode == 'less_than': 
        max_l = max(lengths)
        sum_len = kwargs['sum_length']
        assert max_l <= sum_len,\
            f"There are lines longer ({max_l}) than the specified length {sum_len}"
        return max_l
    err_msg = f"Check rows mode {mode} can only be one of [all_equal, less_than]"
    raise ValueError(err_msg)


def sha256_file(path:str, chunk=1024*1024) -> bytes:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.digest()


def file_meta(path:Path|str) -> dict:
    path = Path(path)
    n_records = sum(1 for _ in open(path, encoding='latin1'))
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
    if not date_match: 
        raise ValueError(f"Path named {path.name} doesnt match date format 'YYYY-MM-DD'")
    date_file = dt.strptime(date_match.group(0), '%Y-%m-%d')
    data_date = date_file.strftime('%y%m%d')
    meta = dict(
        file_name = path.name,
        file_path = str(path),
        file_size = path.stat().st_size,
        file_hash = sha256_file(path),
        n_records = n_records, 
        date_file = date_file, 
        data_date = data_date)
    return meta

