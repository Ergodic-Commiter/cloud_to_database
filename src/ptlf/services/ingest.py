from datetime import datetime as dt
import os 
from pathlib import Path
import re
import zipfile

from ptlf import engine as ee 
from ptlf.core import flow as flw, settings as ss, specs as spx


class Ingestor: 
    def __init__(self, debug:bool=False): 
        self.config = ss.config
        self.debug = debug
        eng_args = ({} if not debug else 
            dict(fast_executemany=False, echo='debug'))
        self.engine = ee.get_engine(self.config, **eng_args)
        self.specs = spx.FieldSpec.dataframe_dict(spx.read_specs())

    PTLF_DAT = re.compile(r"^PTLF_([\d\-]{10})$")
    PTLF_ZIP = re.compile(r"^PRD_TRXS_PTLF_([\d\-]{10}).ZIP$")


    def upload_data(self, path:Path):
        mm_zip = self.PTLF_ZIP.match(path.name)
        if zipfile.is_zipfile(os.fspath(path)) and not mm_zip:
            self._zip_run(path)
        else: 
            self._single_run(path)

    def _single_run(self, path:Path): 
        if self.PTLF_DAT.match(path.name): 
            the_flow = flw.DayDataFlow.from_data(path, debug=self.debug)
            the_flow.run(self.engine, self.specs)
        elif self.PTLF_ZIP.match(path.name): 
            the_flow = flw.DayDataFlow.from_zipfile(path, debug=self.debug)
            the_flow.run(self.engine, self.specs)
        else:
            raise ValueError(f"Path {path.name} doesnt conform to PTLF path forms.")

    def _zip_run(self, path:Path): 
        zip_dir = path.with_suffix('') 
        with zipfile.ZipFile(path) as z: 
            z.extractall(path=zip_dir)
        for ff in zip_dir.iterdir(): 
            self._single_run(ff)


    def reload_data(self, path:Path): 
        the_flow = flw.DayDataFlow.from_data(path, debug=self.debug)
        the_flow.delete_from(self.engine)
        the_flow.run(self.engine, self.specs)


    def delete_date(self, date:dt.date): 
        the_flow = flw.DayDataFlow.from_date(date, self.config.data_loc, debug=self.debug)
        the_flow.delete_from(self.engine)
