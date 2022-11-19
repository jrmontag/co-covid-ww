import fastapi
from starlette.requests import Request

router = fastapi.APIRouter()


@router.get("/")
def index():
    body = """
    <html>
    <body style='padding: 10px;'>
    <h1>📱-friendly CO COVID Wasterwater data</h1>
    <div>
    Try it: <a href='/api/utilities'>/api/utilities</a>
    </div>
    </body>
    </html>
    """
    return fastapi.responses.HTMLResponse(content=body)


@router.get("/api/utilities")
def utilities():
    return {"status": "TODO"}
