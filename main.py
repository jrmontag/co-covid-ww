import argparse
import logging
import fastapi
import uvicorn
from db import process_raw_data, prepare_db
import views


api = fastapi.FastAPI()


def configure_routing():
    api.include_router(views.router)


def load_and_prep_db():
    # start up the thing with:
    # (venv) $ python -i main.py

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # lots of hard-coded constants for now
    in_file = "2022-11-17_ww.json"
    out_file = "2022-11-17_ww.flat.json"
    process_raw_data(in_file, out_file)

    sql_db = "wastewater.db"
    table = "2022-11-17"
    truncate = True
    prepare_db(sql_db, table, out_file, truncate)

    logger.debug("completed db setup")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="reload and prep database", action="store_true")
    args = parser.parse_args()

    if args.db:
        load_and_prep_db()

    configure_routing()

    uvicorn.run(api, port=8888, host="127.0.0.1")
