from importlib.resources import as_file, files
from operator import attrgetter as ɑ, methodcaller as ρ
from pathlib import Path

import pandas as pd
from toolz import functoolz as fz

from ptlf import tools
from ptlf.core import settings
from .converter import Converter




def reload_specs(): 
    cfg = settings.Settings() 
    λ_mutate = dict(
        Name0 = lambda df: df['Field_Name'].str.replace(' ', ''), 
        Name1 = lambda df: tools.index_duplicates(df['Name0']), 
        Format = lambda df: df['Format'].str.replace(' ', ''))
    to_path = Path('src/ptlf/data/ptlf_cols.feather')
    specs_ref = tools.OpenTable(*cfg.xl_ref)
    pre_df = specs_ref.get_dataframe()
    specs_df = (pre_df
        .loc[:, ~pre_df.columns.str.strip().str.endswith('*')]
        .assign(**λ_mutate))
    specs_df.to_feather(to_path)


def read_specs(output='dict') -> dict|pd.DataFrame:
    with as_file(files('ptlf.data')/'ptlf_cols.feather') as ff:
        specs_df = pd.read_feather(ff)
    if output == 'dataframe': 
        return specs_df
    return Converter.dataframe_to_dict(specs_df)


def specs_plus(specs_0):
    attrs = Converter.dataframe_to_dict(specs_0.values())
    meta = dict(
        Name0=ɑ('_specs.Field_Name'),  # corresponds to "Field Name"
        Name1=ɑ('specs.Name1'), 
        pytype=ɑ('pytype.__name__'), 
        mssql=fz.compose_left(ρ('mssql_col'), str))
    λ_meta = fz.juxt(*meta.values())
    attrs_data = list(map(λ_meta, attrs))
    return pd.DataFrame(attrs_data, columns=list(meta.keys()))


def specs_plus_to_excel(specs_1:pd.DataFrame, cfg:settings.Settings=None):
    cfg = cfg or settings.Settings() 
    specs_ref = tools.OpenTable(*cfg.XL_REF)
    _, min_row, max_col, _ = specs_ref.boundaries
    writer_args = dict(engine='openpyxl', mode='a', if_sheet_exists='overlay')  
    excel_args = dict(sheet_name=specs_ref.ws_name, header=True, index=False,
        startrow=min_row-1, startcol=max_col+1)
    with pd.ExcelWriter(specs_ref.wb_path, **writer_args) as xl:
        specs_1.to_excel(xl, **excel_args)    

 