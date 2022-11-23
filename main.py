import argparse
import logging
from pathlib import Path
import fastapi
import uvicorn
from views import home
from api import data_api


def logging_location() -> str:
    log_file = "app.log"
    prod_loc = "/apps/logs/wastewater_api/app_log"
    dev_loc = "data"
    log_loc = Path(dev_loc) / log_file
    if Path(prod_loc).exists():
        log_loc = Path(prod_loc) / log_file
    return str(log_loc)


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(name)s : %(message)s",
    filename=logging_location(),
    level=logging.INFO,
)

api = fastapi.FastAPI()


def configure_routing():
    api.include_router(home.router)
    api.include_router(data_api.router)


if __name__ == "__main__":
    logger.info("> Starting up application")
    configure_routing()
    uvicorn.run(api, port=8888, host="127.0.0.1")
else:
    configure_routing()
