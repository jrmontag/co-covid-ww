import logging
from sqlite3 import Connection
from typing import Iterable

import fastapi
from fastapi import Depends

from models.report import Report
from services import db


logger = logging.getLogger(__name__)
router = fastapi.APIRouter()

API_ROOT = "/api/v1"
DB_URI = "data/wastewater.db"


# dependency
def get_db_conn():
    conn = db.get_connection(DB_URI)
    try:
        yield conn
    finally:
        conn.close()


@router.get(f"{API_ROOT}/utilities")
def utilities(conn: Connection = Depends(get_db_conn)):
    logger.debug(f"Querying utilities")
    results = db.get_utilities(conn)
    if len(results) == 0:
        resp = fastapi.Response(content="Internal error. Please try again later.", status_code=500)
    else:
        resp = {"utilities": results}
    return resp


@router.get(f"{API_ROOT}/samples")
def samples(report: Report = Depends(), conn: Connection = Depends(get_db_conn)):
    results = db.get_samples(conn, report)
    if len(results) == 0:
        resp = fastapi.Response(content="Internal error. Please try again later.", status_code=500)
    else:
        resp = {"parameters": report.dict(), "samples": results}
    return resp


# TODO: endpoint for last_checked and last_data_update
