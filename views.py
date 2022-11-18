import fastapi
from starlette.requests import Request

router = fastapi.APIRouter()


@router.get("/")
def index(request: Request):
    return "hello, CO WW world!"
