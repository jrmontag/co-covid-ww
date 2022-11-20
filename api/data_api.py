import fastapi
from fastapi import Depends
from models.report import Report
from services import db


router = fastapi.APIRouter()

db_conn = db.get_connection("data/wastewater.db")


@router.get("/api/utilities")
def utilities():
    results = db.get_utilities(db_conn)
    resp = {"result": {"utilities": results}}
    return resp


@router.get("/api/samples/{utility}")
def samples(report: Report = Depends()):
    msg = f"called /samples/utility with {report.utility=}, {report.start=}, {report.end=}"
    resp = fastapi.Response(content=msg, status_code=200)
    return resp


@router.get("/api/cases/{utility}")
def cases(report: Report = Depends()):
    msg = f"called /cases/utility with {report.utility=}, {report.start=}, {report.end=}"
    resp = fastapi.Response(content=msg, status_code=200)
    return resp
