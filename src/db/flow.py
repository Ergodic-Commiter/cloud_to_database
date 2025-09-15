from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime as dt, timedelta as delta
from pathlib import Path
from operator import attrgetter as ɑ, methodcaller as ρ
import re
from typing import Optional, Union
import zipfile as zf

from azure.storage.blob import ContainerClient
import pandas as pd
from toolz import curried as cz, dicttoolz as dz, functoolz as fz
import sqlalchemy as alq 
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from src import tools, config as cfg, errors as ee
from src.db import track, utils
from src.db.typer import Typer

# pylint: disable=anomalous-backslash-in-string

@dataclass()
class FlowConfig: 
    date: dt.date   
    work_dir: Path
    zip_file: Optional[str] = None


class DayDataFlow: 
    '''Cloud -> Zip -> File -> DataFrame -> SQL'''
    def __init__(self, config:FlowConfig): 
        self.cfg = config
        self.dates_off = 0
        self.reports = {}

    @property
    def datestr(self):
        return self.cfg.date.strftime('%y%m%d')

    @property
    def datestr2(self):
        return self.cfg.date.strftime('%Y-%m-%d')

    @property
    def datafile(self): 
        return self.at_dir('text')
    
    def at_dir(self, a_dir): 
        wdir = self.cfg.work_dir
        fname = f'PTLF_{self.datestr2}'
        return wdir/a_dir/fname
    
    def get_path(self, which) -> Path: 
        if which == 'data': 
            return self.at_dir('text')
        zip_name = f'PRD_TRXS_PTLF_{self.datestr2}.ZIP'
        if which == 'unzip': 
            return self.at_dir('zips').with_name(zip_name)
        if which == 'cloud': 
            cloud_dir = self.cfg.date.strftime("fiserv/%Y/%-m/%-d")
            return Path(cloud_dir)/zip_name
        if which == 'report': 
            return self.at_dir('failed/1-types').with_suffix('.txt')
        raise ValueError(f"Which Path {which} must be one of [data, unzip, cloud]")
            
    @classmethod
    def from_data(cls, data_file:Path): 
        txt_fmt = r"^(.*)/text/PTLF_([\d\-]{10}$)"
        if (mm := re.match(txt_fmt, str(data_file))) is None: 
            raise ee.PTLF_FlowError(data_file.name, 'DataFileTitle') 
        _workdir, _datestr = mm.groups()
        the_date = dt.strptime(_datestr, '%Y-%m-%d').date()
        the_dir = Path(_workdir)
        return cls(FlowConfig(the_date, the_dir))

    @classmethod
    def from_zipfile(cls, zip_file:Path, missing_ok=False): 
        zip_fmt = r"(.*)/zips/.*/PRD_TRXS_PTLF_([\d\-]{10}).ZIP"
        if (mm := re.match(zip_fmt, str(zip_file))) is None: 
            raise ee.PTLF_FlowError(zip_file.name, 'ZipFileTitle')
            
        _workdir, _datestr = mm.groups()
        the_date = dt.strptime(_datestr, '%Y-%m-%d').date()
        the_dir = Path(_workdir)
        flow = cls(FlowConfig(the_date, the_dir, str(zip_file)))
        flow.extract_zipfile(missing_ok)
        return flow

    def determine_stage(self, engine:Engine, 
            container:Optional[ContainerClient]=None):
        meta = alq.MetaData()
        track_t = alq.Table('PTLF_track', meta, autoload_with=engine)
        hasfile_stmt = (alq.select(track_t)
            .where(track_t.c.file_name == self.datafile.name))
        with engine.begin() as conn: 
            has_file = conn.execute(hasfile_stmt).first() is not None
        if has_file: 
            return 0
        if self.datafile.is_file():
            return 1
        if self.get_path('unzip').is_file(): 
            return 2
        if container is None: 
            return -1 
        the_blob = container.get_blob_client(str(self.get_path('cloud')))
        return 3 if the_blob.exists() else -1 
         
    def run(self, engine:Engine, specs=None, debug=False):
        failpaths = cz.valmap(self.at_dir, dict(
                ConvertTypes='failed/1-types',
                PostingDates='failed/2-dates',
                TrackStart='failed/3-start', 
                RawUpload='failed/4-upload', 
                TrackEnd='failed/5-end'))
        if specs is None: 
            specs = read_specs()
        
        data_df = self.read_data(specs)
        if self.reports.get('ReadData'):
            print("Errors when reading data")
            report_str = str(dict(self.reports['ReadData'])) 
            self.get_path('report').write_text(report_str)
        try:
            self.upload_data(data_df, engine, debug)
        except ee.PTLFUploadError as er:
            print("Error when uploading") 
            self.datafile.replace(failpaths[er.reason])
        else:
            self.datafile.unlink()


    def download_cloud(self, container:ContainerClient): 
        zip_name = f'PRD_TRXS_PTLF_{self.datestr2}.ZIP'
        blob_dir = self.cfg.date.strftime("fiserv/%Y/%-m/%-d")
        blob_from = f"{blob_dir}/{zip_name}"
        zip_to = self.at_dir('zips').with_name(zip_name)
        with open(zip_to, 'wb') as f:
            blob_stream = container.download_blob(blob_from)
            f.write(blob_stream.readall())  
        self.cfg.zip_file = str(zip_to)


    def extract_zipfile(self, missing_ok=False):
        zipfile = self.cfg.zip_file or str(self.get_path("unzip")) 
        if not zf.is_zipfile(zipfile) and missing_ok: 
            return
        to_unzip = self.get_path('data') 
        with zf.ZipFile(zipfile, 'r') as zz: 
            zz.extract(to_unzip.name, path=to_unzip.parent)
        Path(zipfile).unlink()


    def read_data(self, specs=None, debug=False) -> pd.DataFrame: 
        if specs is None: 
            specs = read_specs()
        fwf_args = dict(dtype=str, header=None, colspecs=[(0, None)], 
            names=['value'])
        reporter = defaultdict(list)
        λ_fromrow = ρ('pd_fromrow', row_name='value', report=reporter)
        mutates = dz.valmap(λ_fromrow, specs)
        df_0 = pd.read_fwf(self.datafile, encoding='latin1', **fwf_args)
        if debug: 
            return df_0
        df_1 = pd.DataFrame({nm: λλ(df_0) for nm, λλ in mutates.items()})
        self.reports['ReadData'] = reporter
        df_key = df_1['NGBBSE24-AUTH-POST-DAT']
        if (df_key != df_key[0]).all(): 
            raise ee.PTLF_FlowError(self.datafile.name, 'PostingDates') 
        data_date = dt.strptime(df_key[0], '%y%m%d').date()
        self.dates_off = (data_date - self.cfg.date).days
        return df_1

    
    def upload_data(self, a_df:pd.DataFrame, engine:Engine, debug=False): 
        sql_params = dict(con=engine, schema='dbo', 
            if_exists='append', name='PTLF_raw', index=False)
        sql_params |= dict(method=None, chunksize=1) if debug else {}

        meta = utils.file_meta(self.datafile)
        if self.dates_off: 
            data_date = self.cfg.date + delta(days=self.dates_off)
            meta['data_date'] = data_date.strftime('%y%m%d')
        try: 
            an_id = track.start_raw(engine, meta)
        except IntegrityError as er:
            raise ee.PTLF_FlowError(self.datafile.name, 'TrackStart') from er
        status = 'failed'
        try:
            a_df.to_sql(**sql_params)
            status = 'success'
        except Exception as er:
            raise ee.PTLFUploadError(self.datafile.name, 'RawUpload') from er
        finally: 
            track.finish_raw(engine, an_id, status)

    def __repr__(self): 
        return f"<DayDataFlow at {self.datafile.name}>"


#### Specs Stuff

def read_specs(output='dict') -> Union[dict, pd.DataFrame]:
    # Antes regresaba el DataFrame, pero es mejor el dccionario convertido.
    specs_ref = tools.OpenTable(*cfg.XL_REF)
    specs_df = specs_ref.get_dataframe()
    if output == 'dataframe': 
        return specs_df
    return Typer.dataframe_to_dict(specs_df)


def specs_plus(specs_0):
    attrs = Typer.dataframe_to_dict(specs_0.values())
    meta = dict(
        Name0=ɑ('_specs.Field_Name'),  # corresponds to "Field Name"
        Name1=ɑ('specs.Name1'), 
        pytype=ɑ('pytype.__name__'), 
        mssql=fz.compose_left(ρ('mssql_col'), str))
    λ_meta = fz.juxt(*meta.values())
    attrs_data = list(map(λ_meta, attrs))
    return pd.DataFrame(attrs_data, columns=list(meta.keys()))


def specs_plus_to_excel(specs_1): 
    file, sheet, table = cfg.XL_REF
    specs_ref = tools.OpenTable(file, sheet, table)
    _, min_row, max_col, _ = specs_ref.boundaries
    writer_args = dict(engine='openpyxl', mode='a', if_sheet_exists='overlay')  
    excel_args = dict(sheet_name=sheet, startrow=min_row-1, startcol=max_col+1, 
        header=True, index=False)
    with pd.ExcelWriter(file, **writer_args) as xl:
        specs_1.to_excel(xl, **excel_args)    


def files_to_dataframe(data_dir=None): 
    data_dir = data_dir or Path(cfg.DATA_LOC/'temp')
    ptlf_gen = map(utils.file_meta, data_dir.rglob("PTLF_[0-9-]*"))
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