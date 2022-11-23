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


@router.get("/api/utilities")
def utilities():
    if db_conn:
        results = db.get_utilities(db_conn)
        resp = {"utilities": results}
    else:
        logger.error("Database connection is missing")
        resp = fastapi.Response(
            content="Internal error. Please try again later.", status_code=500
        )
    return resp


@router.get("/api/samples/{utility}")
def samples(report: Report = Depends()):
    msg = f"called /samples/utility with {report.utility=}, {report.start=}, {report.end=}"
    logger.debug(f"Called /api/samples/{report.utility}")
    resp = fastapi.Response(content=msg, status_code=200)
    return resp


@router.get("/api/cases/{utility}")
def cases(report: Report = Depends()):
    msg = (
        f"called /cases/utility with {report.utility=}, {report.start=}, {report.end=}"
    )
    resp = fastapi.Response(content=msg, status_code=200)
    return resp
