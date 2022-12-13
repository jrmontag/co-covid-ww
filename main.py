import argparse
import logging
from pathlib import Path

import fastapi
from starlette.staticfiles import StaticFiles
import uvicorn

from views import home
from api import data_api


api = fastapi.FastAPI()


def configure_routing():
    api.include_router(home.router)
    api.include_router(data_api.router)
    api.mount("/static", StaticFiles(directory="static"), name="static")


def configure_logging(env="prod") -> logging.Logger:
    logger = logging.getLogger(__name__)
    log_level = logging.INFO if env == "prod" else logging.DEBUG

    def logging_location() -> str:
        log_file = "app.log"
        prod_loc = "/apps/logs/wastewater_api/app_log"
        dev_loc = "data"
        log_loc = Path(dev_loc) / log_file
        if Path(prod_loc).exists():
            log_loc = Path(prod_loc) / log_file
        return str(log_loc)

    logging.basicConfig(
        format="%(asctime)s : %(levelname)s : %(name)s : %(message)s",
        filename=logging_location(),
        level=log_level,
    )
    return logger


if __name__ == "__main__":
    logger = configure_logging(env="dev")
    logger.info("> Starting application from CLI")
    configure_routing()
    uvicorn.run(api, port=8888, host="127.0.0.1")
else:
    # TODO: set this to prod eventually
    logger = configure_logging(env="dev")
    logger.info("> Starting application from systemd and gunicorn")
    configure_routing()
