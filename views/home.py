import fastapi
from starlette.requests import Request

router = fastapi.APIRouter()


@router.get("/")
def index():
    body = """
    <html>
    <body style='padding: 10px;'>
    <h1>(eventually) 📱-friendly CO COVID Wasterwater data</h1>
    <div>
    See available reporting utilities: <a href='/api/utilities'>/api/utilities</a>
    </div>
    <div>
    Check Denver-area wastewater measurements: <a href='/api/samples'>/api/samples</a>
    </div>
    </body>
    </html>
    """
    return fastapi.responses.HTMLResponse(content=body)

