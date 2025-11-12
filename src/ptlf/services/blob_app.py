import azure.functions as func
from azurefunctions.extensions.bindings import blob

from ptlf.infra import get_logger
from ptlf.core import errors as ee, settings, flow, engine

cfg = settings.Settings()
alq_eng = engine.get_engine(cfg)



app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
@app.function_name(name="PTLF-Blob-To-SQL")
@app.blob_trigger(arg_name="a_blob", 
    path="%STORAGE_CONTAINER%/fiserv/{date1}/PRD_TRXS_PTLF_{date2}.ZIP", 
    connection="BlobConn")
def blob_trigger(a_blob: blob.BlobClient):
    logger = get_logger("func.blob_ingest", blob=a_blob.name)
    logger.info("Downloading Blob %s", a_blob.blob_name)
    try:
        the_flow = flow.DayDataFlow.from_blob_client(a_blob, logger=logger)
    except ee.PTLF_FlowError as er:
        logger.exception("Bad blob name or format; skipping: %s", a_blob.blob_name)
        raise er
    the_flow = flow.DayDataFlow.from_blob_client(a_blob, logger=logger)
    the_flow.extract_zipfile()
    the_flow.run(alq_eng)
    logger.info("Blob %s successful", a_blob.blob_name)


    