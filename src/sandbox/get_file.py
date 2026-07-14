from datetime import datetime as dt
from sys import argv
import zipfile as zp

import infra

# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

def download_fpsl(container, date_str): 
    a_date = dt.strptime(date_str, '%Y-%m-%d').date()
    file_from = 'fiserv/{0.year}/{0.month}/{0.day}/PRD_TRXS_PTLF_{0}.ZIP'.format(a_date)
    file_to = f'data/temp/zips/PTLF_{a_date}.ZIP'
    print(f"Downloading: {file_from}")
    with open(file_to, 'wb') as f: 
        f.write(container.download_blob(file_from).readall())

def unzip_fpsl(date_str): 
    file_from = f'data/temp/zips/PTLF_{date_str}.ZIP'
    file_to = 'data/temp/text'
    with zp.ZipFile(file_from, 'r') as f: 
        f.extractall(path=file_to)


if __name__ == '__main__': 
    today_str = str(dt.today().date())
    date_str = argv[1] if len(argv) > 1 else today_str
    fpsl_file = f'data/temp/PTLF_{date_str}'
    az_container = infra.get_container()
    download_fpsl(az_container, date_str)
    # unzip_fpsl(date_str)



