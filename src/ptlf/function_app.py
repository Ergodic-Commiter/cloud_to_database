import logging

import azure.functions as func
from azurefunctions.extensions.bindings import blob

from ptlf.config import Settings
from ptlf import flow, engine, local_logging

cfg = Settings()
alq_eng = engine.get_engine(cfg)
local_logging.setup(cfg)


class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        ctx = " ".join(f"{k}={v}" for k,v in self.extra.items())
        return f"{msg} | {ctx}", kwargs

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
@app.function_name(name="PTLF-Blob-To-SQL")
@app.blob_trigger(arg_name="a_blob", 
    path="%STORAGE_CONTAINER%/fiserv/{date1}/PRD_TRXS_PTLF_{date2}.ZIP", 
    connection="AzureWebJobsStorage")
def blob_trigger(a_blob: blob.BlobClient):
    logbase = logging.getLogger("ptlf-blob-to-sql")
    logger = ContextAdapter(logbase, {"blob": a_blob.blob_name})
    logger.info("Downloading Blob %s", a_blob.blob_name)
    
    the_flow = flow.DayDataFlow.from_blob_client(a_blob, logger=logger)
    the_flow.extract_zipfile()
    the_flow.run(alq_eng)
    logger.info("Blob %s successful", a_blob.blob_name)


    