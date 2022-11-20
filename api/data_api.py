import fastapi
from fastapi import Depends
from models.observation import Observation


router = fastapi.APIRouter()


@router.get("/api/utilities")
def utilities():
    return fastapi.Response(content="called /utilities", status_code=200)


@router.get("/api/samples/{utility}")
def samples(obs: Observation = Depends()):
    msg = f"called /samples/utility with {obs.utility=}, {obs.start=}, {obs.end=}"
    resp = fastapi.Response(content=msg, status_code=200)
    return resp


@router.get("/api/cases/{utility}")
def cases(obs: Observation = Depends()):
    msg = f"called /cases/utility with {obs.utility=}, {obs.start=}, {obs.end=}"
    resp = fastapi.Response(content=msg, status_code=200)
    return resp
