import argparse
import logging
import fastapi
import uvicorn
from views import home
from api import data_api


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

api = fastapi.FastAPI()


def configure_routing():
    api.include_router(home.router)
    api.include_router(data_api.router)


if __name__ == "__main__":
    configure_routing()
    uvicorn.run(api, port=8888, host="127.0.0.1")
