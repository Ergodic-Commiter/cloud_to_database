import re
import pandas as pd
import sqlalchemy as alq
from sqlalchemy.dialects import mssql

from src.tools import read_excel_table





def parse_format(fmt_str:str):
    reg_fmt = r"^(S?9|X)(?:\((\d{1,4})\))?(?:V9(\d))?"
    if not (reg_match := re.match(reg_fmt, fmt_str.strip().upper())):
        raise ValueError(f"Format string '{fmt_str}' cannot be parsed.")        
    base0, len0, v9 = reg_match.groups()
    if base0 == 'X':
        return mssql.VARCHAR(int(len0 or 1))
    if base0 in ('9', 'S9'):
        len1 = int(len0 or 1)
        dec1 = int(v9 or 0)
        prec = len1 + dec1
        scale = dec1 
        return mssql.DECIMAL(prec, scale)
    raise ValueError(f"Format string '{fmt_str}' cannot parse base '{base_type}'.")


def row_to_colspec(t_row:tuple): 
    try: 
        r_name = t_row.Name1    # Matches λ_mutate below.  
        r_format = parse_format(t_row.Format)
        r_comment = t_row.Description
        return alq.Column(r_name, r_format, comment=r_comment)
    except Exception as e: 
        e_msg = f"Error with row: {t_row}\n\nOriginal error: {e}"
        raise ValueError(e_msg) from e
    

def index_duplicates(srs:pd.Series):
    duplicates = srs.duplicated(False)
    occurrence = srs.groupby(srs).cumcount() + 1
    suffix = ('_' + occurrence.astype(str)).where(duplicates, '')
    return srs+suffix


