import os
from pathlib import Path
import re
from sys import argv
from time import time
import zipfile

from ptlf import core, services, tools
from ptlf.core import errors as ee, models
# pylint:disable=invalid-name

fspath = tools.noner(os.fspath)
is_ptlf_zip = lambda pp: re.search(r"(PTLF_[\d-]{10}).ZIP", fspath(pp))


def to_zip_or_dir(pathish:Path) -> Path: 
    pathish = Path(pathish)    
    if pathish.is_dir():
        assert next(filter(is_ptlf_zip, pathish.iterdir())),\
            f"DirPath '{pathish}' doesnt seem to have ptlf zips." 
        return pathish
    if zipfile.is_zipfile(pathish):
        zip_dir = pathish.with_suffix('') 
        with zipfile.ZipFile(pathish) as z: 
            zip_names = list(filter(is_ptlf_zip, z.namelist()))
            assert len(zip_names) > 0,\
                f"ZipFile '{pathish}' doesnt seem to have ptlf zips." 
            z.extractall(path=zip_dir, members=zip_names)
        return zip_dir
    raise ValueError(f"Path '{pathish}' must be a zipfile")



if __name__ == '__main__': 
    zip_or_dir = argv[1] if len(argv) > 1 else None
    debug = (len(argv) > 2) and (argv[2] == 'debug')
    if zip_or_dir is None: 
        raise ValueError("Please include folder or zipfile argument.")
    a_dir = to_zip_or_dir(zip_or_dir)

    cfg = core.Settings()
    eng_args = dict(fast_executemany=False, echo='debug') if debug else {}
    alq_eng = core.get_engine(cfg, **eng_args)

    specs_dict = models.read_specs()
    zips = list(filter(is_ptlf_zip, Path(a_dir).iterdir()))
    time0 = time()
    for ll, lilzip in enumerate(zips):
        try: 
            lilflow = services.DayDataFlow.from_zipfile(lilzip, debug=debug)
            lilflow.run(alq_eng, specs_dict)
        except ee.ErrorControversias as err: 
            ... 
        print(f"Process file {ll} of {len(zips)}: {lilzip.stem}")
        print(f"\tElapsed time: {time() - time0:.2f} seconds")
        time0 = time()

        
