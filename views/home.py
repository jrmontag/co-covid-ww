import logging
import fastapi
from starlette.requests import Request

router = fastapi.APIRouter()

logger = logging.getLogger(__name__)

@router.get("/")
def index():
    logger.debug('Rendering home page at /')
    body = """
    <html>
    <body style='padding: 10px;'>
    <h1>API-based CO COVID Wasterwater data</h1>
    <div>
    See <a href='/api/v1/utilities'>available reporting utilities</a>
    </div>
    
    <div>
    Check recent <a href='/api/v1/samples'>Denver-area measurements</a>
    </div>
    
    <div>
    Check <a href='/api/v1/samples?utility=Boulder&start=2022-08-01&end=2022-08-31'>August Boulder-area measurements</a>
    </div>
    </body>
    </html>
    """
    return fastapi.responses.HTMLResponse(content=body)
