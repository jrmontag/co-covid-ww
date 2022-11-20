import logging
import sqlite3
import fastapi
from fastapi import Depends
from models.report import Report
from services import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = fastapi.APIRouter()

try:
    db_conn = db.get_connection("data/wastewater.db")
except sqlite3.OperationalError as oe:
    logging.error(f"DB error: {oe}")


@router.get("/api/utilities")
def utilities():
    try:
        results = db.get_utilities(db_conn)
    except sqlite3.OperationalError as oe:
        logging.warning(f"database error: {oe}")
        return fastapi.Response(
            content="Internal error. Please try again later.", status_code=500
        )
    resp = {"result": {"utilities": results}}
    return resp


@router.get("/api/samples/{utility}")
def samples(report: Report = Depends()):
    msg = f"called /samples/utility with {report.utility=}, {report.start=}, {report.end=}"
    resp = fastapi.Response(content=msg, status_code=200)
    return resp


@router.get("/api/cases/{utility}")
def cases(report: Report = Depends()):
    msg = (
        f"called /cases/utility with {report.utility=}, {report.start=}, {report.end=}"
    )
    resp = fastapi.Response(content=msg, status_code=200)
    return resp
