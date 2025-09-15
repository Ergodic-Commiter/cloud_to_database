from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime as dt, timedelta as delta
import logging
from pathlib import Path
from operator import methodcaller as ρ
import re
from typing import Optional
import zipfile as zf

from azure.storage.blob import ContainerClient, BlobClient
import pandas as pd
from toolz import dicttoolz as dz
import sqlalchemy as alq 
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, OperationalError

from src.config import Settings
from src.ptlf import track, utils, errors as ee, typer

# pylint: disable=anomalous-backslash-in-string


@dataclass()
class FlowConfig: 
    date: dt.date   
    work_dir: Path
    zip_file: Optional[str] = None


class DayDataFlow: 
    '''Cloud -> Zip -> File -> DataFrame -> SQL'''
    def __init__(self, config:FlowConfig, logger:Optional[logging.Logger]=None): 
        self.cfg = config
        self.dates_off = 0
        self.reports = {}
        self.log = logger or logging.getLogger('__name__')
    
    # Pasada la inicialización, las funciones se enlistan de alto nivel a bajo nivel. 
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
            raise ee.PTLF_FlowError(zip_file.name, 'ZipFileName')
            
        _workdir, _datestr = mm.groups()
        the_date = dt.strptime(_datestr, '%Y-%m-%d').date()
        the_dir = Path(_workdir)
        flow = cls(FlowConfig(the_date, the_dir, str(zip_file)))
        flow.extract_zipfile(missing_ok)
        return flow

    @classmethod
    def from_blob_client(cls, blob:BlobClient, logger:logging.Logger):
        cfg = Settings()

        blob_reg = r"mediospago/fiserv/([\d/]{8,10})/PRD_TRXS_PTLF_([\d\-]{10}).ZIP"
        if (mm := re.match(blob_reg, blob.blob_name) is None): 
            raise ee.PTLF_FlowError(blob.blob_name, 'BlobName')
        _, date2 = mm.groups()
        the_date = dt.strptime(date2, '%Y-%m-%d').date()
        the_flow = cls(FlowConfig(the_date, cfg.data_loc), logger=logger)
        down_to = the_flow.get_path('unzip')
        down_to.parent.mkdir(parents=True, exist_ok=True)
        with open(down_to, 'wb') as f:
            blob_stream = blob.download_blob()
            f.write(blob_stream.readall())  
        the_flow.cfg.zip_file = str(down_to)
        return the_flow


    def run(self, engine:Engine, specs=None, debug=False):
        """Este proceso se encarga del procesamiento de carga. 
        Además es el único donde se hace error-handling."""
        if specs is None: 
            specs = typer.read_specs()
        try:
            data_df = self.read_data(specs)
        except ee.PTLF_FlowError as er:
            self.log.error("ReadData error in %s", er.event) 

        if self.reports.get('ReadData'):
            self.log.warning("Check types in ReadData:")
            report_str = str(dict(self.reports['ReadData'])) 
            self.log.info(report_str)
        try:
            self.upload_data(data_df, engine, debug)
        except ee.PTLF_FlowError as er:
            self.log.error("Upload error at %s", er.event)
        finally:
            self.datafile.unlink()


    def download_cloud(self, container:ContainerClient): 
        blob_from = str(self.get_path('cloud'))
        zip_to = self.get_path('unzip')
        with open(zip_to, 'wb') as f:
            blob_stream = container.download_blob(blob_from)
            f.write(blob_stream.readall())  
        self.cfg.zip_file = str(zip_to)


    def extract_zipfile(self, missing_ok=False): 
        unzip_from = self.get_path('unzip')
        data_to = self.get_path('data')
        if not zf.is_zipfile(str(unzip_from)) and missing_ok: 
            return 
        with zf.ZipFile(str(unzip_from), 'r') as zz: 
            zz.extract(data_to.name, path=data_to.parent)
        unzip_from.unlink()


    def read_data(self, specs=None, debug=False) -> pd.DataFrame: 
        if specs is None: 
            specs = typer.read_specs()
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
            raise ee.PTLF_FlowError(self.datafile.name, 'TrackIntegrity') from er
        status = 'failed'
        try:
            a_df.to_sql(**sql_params)
            status = 'success'
        except Exception as er:
            raise ee.PTLF_FlowError(self.datafile.name, 'RawUpload') from er
        finally: 
            track.finish_raw(engine, an_id, status)

    def determine_stage(self, engine:Engine, 
            container:Optional[ContainerClient]=None):
        meta = alq.MetaData()
        try: 
            track_t = alq.Table('PTLF_track', meta, autoload_with=engine)
        except OperationalError as er:
            raise ee.PTLFConnError('AutoloadTable_CheckConnection') from er
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
         

    # Funciones y propiedades utilitarias.
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

    def __repr__(self): 
        return f"<DayDataFlow at {self.datafile.name}>"



def files_to_dataframe(data_dir:Optional[Path]=None): 
    data_dir = data_dir or Path('data/temp')
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