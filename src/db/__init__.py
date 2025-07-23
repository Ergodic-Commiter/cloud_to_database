from itertools import starmap
import sqlalchemy as alq
from sqlalchemy.engine import URL
from toolz import functoolz as fz

from ..tools import partial2
from .. import config as cfg


db_params = cfg.db_params()
conn_str = ''.join('{}={};'.format(*k_v) 
        for k_v in db_params.items())
conn_qry = {'odbc_connect': conn_str}
conn_url = URL.create('mssql+pyodbc', query=conn_qry)
engine = alq.create_engine(conn_url)
# engine = fz.pipe(cfg.db_params().items(), 
#     partial2(starmap, "{}={};".format), ''.join, 
#     partial2(dict, odbc_connect=...), 
#     partial2(URL.create, "mssql+pyodbc", query=...), 
#     alq.create_engine)
 
metadata = alq.MetaData()

