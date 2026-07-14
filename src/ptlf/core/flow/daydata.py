from dataclasses import dataclass
from datetime import datetime as dt, timedelta as delta
import logging
from pathlib import Path
import os
import re
from typing import Self
import zipfile as zf

from azure.storage.blob import ContainerClient, BlobClient
import pandas as pd
import sqlalchemy as alq 
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, OperationalError
from toolz import dicttoolz as dz

from ptlf import settings as ss, tools
from ptlf.core import errors as ee, flow as flw, specs as spx

fspath = tools.noner(os.fspath)
# pylint: disable=anomalous-backslash-in-string
# pylint: disable=too-many-locals


@dataclass()
class FlowConfig: 
    date: dt.date   
    work_dir: Path
    zip_path: Path|None = None
    debug: bool = False


class DayDataFlow: 
    '''Cloud -> Zip -> File -> DataFrame -> SQL'''
    _TEXT_FMT = re.compile(r"^(.*)/text/PTLF_([\d\-]{10}$)")
    _ZIP_FMT = re.compile(r"(.*)/zips/(.*/)?PRD_TRXS_PTLF_([\d\-]{10}).ZIP")
    _BLOB_FMT = re.compile(r"^fiserv/([\d/]{5,10})/PRD_TRXS_PTLF_([\d\-]{10}).ZIP$")

    def __init__(self, config:FlowConfig, logger:logging.Logger=None): 
        self.cfg = config
        self.dates_off = 0
        self.log = logger or logging.getLogger('__name__')
        self.reports = {}
    
    @classmethod
    def from_date(cls, date:dt.date, work_dir:Path, debug:bool=False) -> Self:
        return cls(FlowConfig(date, work_dir, None, debug)) 
        

    # Pasada la inicialización, las funciones se enlistan de alto nivel a bajo nivel. 
    @classmethod
    def from_data(cls, data_file:Path, debug=False) -> 'DayDataFlow': 
        if (data_match := cls._TEXT_FMT.match(fspath(data_file))) is None: 
            raise ee.PTLF_FlowError(data_file.name, 'DataFileTitle') 
        _workdir, _datestr = data_match.groups()
        the_date = dt.strptime(_datestr, '%Y-%m-%d').date()
        the_dir = Path(_workdir)
        return cls(FlowConfig(the_date, the_dir, None, debug))

    @classmethod
    def from_zipfile(cls, zip_file:Path, missing_ok=False, debug=False) -> Self: 
        if (zip_match := cls._ZIP_FMT.match(fspath(zip_file))) is None: 
            raise ee.PTLF_FlowError(zip_file.name, 'ZipFileName')
        _workdir, _, _datestr = zip_match.groups()
        the_date = dt.strptime(_datestr, '%Y-%m-%d').date()
        the_dir = Path(_workdir)
        flow = cls(FlowConfig(the_date, the_dir, zip_file, debug))
        flow.extract_zipfile(missing_ok)
        return flow

    @classmethod
    def from_blob_client(cls, blob:BlobClient, 
        *, logger:logging.Logger=None, debug=False) -> Self:
        out_cfg = ss.config
        at_data = out_cfg.data_loc

        if (blob_match := cls._BLOB_FMT.match(blob.blob_name)) is None:
            logger.info("ACC=%s, CONT=%s, NAME=%s", 
                blob.account_name, blob.container_name, blob.blob_name) 
            raise ee.PTLF_FlowError(blob.blob_name, 'BlobName')
        _datepath, date2 = blob_match.groups()
        the_date = dt.strptime(date2, '%Y-%m-%d').date()
        in_cfg = FlowConfig(the_date, at_data, None, debug)
        
        the_flow = cls(in_cfg, logger=logger)
        down_to = the_flow.get_path('unzip')
        down_to.parent.mkdir(parents=True, exist_ok=True)
        with open(down_to, 'wb') as f:
            blob_stream = blob.download_blob()
            f.write(blob_stream.readall())  
        the_flow.cfg.zip_path = down_to
        return the_flow


    def run(self, engine:Engine, specs=None):
        if specs is None: 
            specs_df = spx.read_specs()
            specs = spx.FieldSpec.dataframe_dict(specs_df)
        try:
            data_df = self.read_data(specs)
        except ee.PTLF_FlowError as er:
            self.log.error("ReadData error in %s", er.event) 

        if self.reports.get('ReadData'):
            self.log.warning("Check types in ReadData:")
            report_str = str(dict(self.reports['ReadData'])) 
            self.log.info(report_str)
        try:
            self.upload_data(data_df, engine)
        except ee.PTLF_FlowError as er:
            self.log.error("Upload error at %s", er.event)


    def delete_from(self, engine:Engine): 
        flw.delete_raw(engine, self.datestr)


    def clean_up(self, status): 
        pass 


    def download_cloud(self, container:ContainerClient): 
        blob_from = fspath(self.get_path('cloud'))
        zip_to = self.get_path('unzip')
        with open(fspath(zip_to), 'wb') as f:
            blob_stream = container.download_blob(blob_from)
            f.write(blob_stream.readall())  
        self.cfg.zip_file = zip_to


    def extract_zipfile(self, missing_ok=False) -> None: 
        unzip_from = self.cfg.zip_path or self.get_path('unzip')
        data_to = self.get_path('data')
        if not zf.is_zipfile(fspath(unzip_from)) and missing_ok: 
            return 
        with zf.ZipFile(fspath(unzip_from), 'r') as zz: 
            zz.extract(data_to.name, path=data_to.parent)
        

    def read_data(self, specs=None) -> pd.DataFrame: 
        if specs is None: 
            specs_df = spx.read_specs()
            specs = spx.FieldSpec.dataframe_dict(specs_df)
        intakes = dz.valmap(spx.PandasIntake.from_spec, specs)
        mutates = dz.valmap(lambda take: take.make_lambda(), intakes)

        fwf_args = dict(dtype=str, header=None, colspecs=[(0, None)], names=['value'])
        df_0 = pd.read_fwf(self.datafile, encoding='latin1', **fwf_args)['value']
        df_1 = pd.DataFrame({nm: λλ(df_0) for nm, λλ in mutates.items()})
        
        date_key = df_1['NGBBSE24-AUTH-POST-DAT']
        if not (date_key == date_key[0]).all(): 
            raise ee.PTLF_FlowError(self.datafile.name, 'PostingDatesNotEqual')
        the_date = dt.strptime(date_key[0], '%y%m%d').date()
        self.dates_off = (the_date - self.cfg.date).days
        return df_1

    
    def upload_data(self, a_df:pd.DataFrame, engine:Engine): 
        sql_params = dict(con=engine, schema='dbo', 
            if_exists='append', name='PTLF_raw', index=False)
        sql_params |= dict(method=None, chunksize=1) if self.cfg.debug else {}

        meta = tools.file_meta(self.datafile)
        if self.dates_off: 
            data_date = self.cfg.date + delta(days=self.dates_off)
            meta['data_date'] = data_date.strftime('%y%m%d')
        try: 
            an_id = flw.start_raw(engine, meta)
        except IntegrityError as e1:
            raise ee.PTLF_FlowError(self.datafile.name, 'TrackIntegrity') from e1
        status = 'failed'
        try:
            a_df.to_sql(**sql_params)
            status = 'success'
        except Exception as e1:
            raise ee.PTLF_FlowError(self.datafile.name, 'RawUpload') from e1
        finally: 
            flw.finish_raw(engine, an_id, status)


    def determine_stage(self, engine:Engine, container:ContainerClient=None):
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
            self.log.info("Track table contains %s."%self.datafile.name) 
            return 0
        if self.datafile.is_file():
            filename = self.datafile.name
            self.log.info("Datafile %s exists.", filename)
            return 1
        if self.get_path('unzip').is_file(): 
            zip_name = self.get_path('unzip').name
            self.log.info("Logfile %s exists.", zip_name)
            return 2
        if container is None: 
            self.log.info("Cannot connect to container.")
            return -1 
        the_blob = container.get_blob_client(fspath(self.get_path('cloud')))
        if the_blob.exists():
            cloud_name = self.get_path('cloud').name
            self.log.info("Found Blob at: %s", cloud_name)
            return 3
        
        cloud_name = self.get_path('cloud').name
        self.log.info("No blob found at %s", cloud_name)
        return -1
         

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
    
    def at_dir(self, a_dir) -> Path: 
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

