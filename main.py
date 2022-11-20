import argparse
import logging
import fastapi
import uvicorn
from services.db import process_raw_data, prepare_db
from views import home
from api import data_api


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

api = fastapi.FastAPI()


def configure_routing():
    api.include_router(home.router)
    api.include_router(data_api.router)


def load_and_prep_db():
    # lots of hard-coded constants for now
    data_dir = "data"
    in_file = f"{data_dir}/2022-11-17_ww.json"
    out_file = f"{data_dir}/2022-11-17_ww.flat.json"
    process_raw_data(in_file, out_file)

    sql_db = f"{data_dir}/wastewater.db"
    table = "2022-11-17"
    truncate = True
    prepare_db(sql_db, table, out_file, truncate)

    logger.debug("completed db setup")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_db", help="reload and prep database", action="store_true"
    )
    # TODO: arg for launching cron?
    args = parser.parse_args()

    if args.build_db:
        load_and_prep_db()

    configure_routing()

    uvicorn.run(api, port=8888, host="127.0.0.1")
