from pathlib import Path
import re
from sys import argv
from time import time
import zipfile

from src.ptlf import flow, engine, errors as ee
# pylint:disable=invalid-name

is_ptlf_zip = lambda pp: re.compile(r"(PTLF_[\d-]{10}).ZIP").search(str(pp))


def to_zip_or_dir(pathish:Path|str) -> Path: 
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
    if zip_or_dir is None: 
        raise ValueError("Please include folder or zipfile argument.")
    a_dir = to_zip_or_dir(zip_or_dir)
    
    debug = (len(argv) > 2) and (argv[2] == 'debug')
    eng_args = dict(fast_executemany=False, echo='debug') if debug else {}
    alq_eng = engine.get_engine(**eng_args)

    specs_dict = flow.read_specs()
    zips = list(filter(is_ptlf_zip, Path(a_dir).iterdir()))
    time0 = time()
    for ll, lilzip in enumerate(zips):
        try: 
            lilflow = flow.DayDataFlow.from_zipfile(lilzip)
            lilflow.run(alq_eng, specs_dict, debug)
        except ee.ErrorControversias as err: 
            ... 
        print(f"Process file {ll} of {len(zips)}: {lilzip.stem}")
        print(f"\tElapsed time: {time() - time0:.2f} seconds")
        time0 = time()

        
