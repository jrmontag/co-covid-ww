import logging
import sqlite3
from typing import Optional
import fastapi
from fastapi import Depends
from models.report import Report
from services import db

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()

db_conn: Optional[sqlite3.Connection] = db.get_connection("data/wastewater.db")

API_ROOT = "/api/v1"

@router.get(f"{API_ROOT}/utilities")
def utilities():
    if db_conn:
        logger.debug(f"Found db connection, querying utilities")
        results = db.get_utilities(db_conn)
        resp = {"utilities": results}
    else:
        logger.error("Database connection is missing")
        resp = fastapi.Response(
            content="Internal error. Please try again later.", status_code=500
        )
    return resp


@router.get(f"{API_ROOT}/samples")
def samples(report: Report = Depends()):
    if db_conn:
        logger.debug(f"Found db connection, querying samples with {report=}")
        results = db.get_samples(db_conn, report)
        resp = {"parameters": report.dict(), "samples": results}
    else:
        logger.error("Database connection is missing")
        resp = fastapi.Response(
            content="Internal error. Please try again later.", status_code=500
        )
    return resp
