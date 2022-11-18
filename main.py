import logging
from db import process_raw_data, prepare_db


def main():
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

    logger.debug("done!")


if __name__ == "__main__":
    main()
