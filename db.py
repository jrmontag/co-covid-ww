import json
import logging
from pathlib import Path
import sqlite3
from typing import List, Optional
from dateutil import parser
from sqlite_utils import Database

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def process_raw_data(raw_file: str, out_file: Optional[str] = None) -> None:
    # convert downloaded json to appropriate for for bulk load, write
    logger.debug(f"reading input file {raw_file}")
    ww_raw_content: str = Path(raw_file).read_text()
    ww = json.loads(ww_raw_content)
    try:
        features: List[dict] = ww["features"]
    except KeyError as ke:
        raise Exception(
            f"input data did not match expected schema. observed keys: {ww.keys()}"
        )

    flat_features: List[dict] = []
    for i, feature in enumerate(features):
        flat_feature: dict = feature["attributes"]
        del flat_feature["ObjectId"]
        flat_features.append(flat_feature)
    logger.debug(f"observed {i} features")

    if not out_file:
        file_date: str = raw_file[:10]
        out_file: str = f"{file_date}_ww.flat.json"
    logger.debug(f"writing output file {out_file}")
    Path(out_file).write_text(json.dumps(flat_features))


def prepare_db(
    database: str, table: str, data_file: str, truncate: Optional[bool] = False
) -> None:
    # bulk insert data, reformat dates, create index
    table_data: List[dict] = json.loads(Path(data_file).read_text())
    logger.debug(
        f"loading {table=} into {database=} from {data_file=}, {'yes' if truncate else 'not'} dropping content"
    )
    db = Database(database)
    db[table].insert_all(records=table_data, truncate=truncate)

    # MM/DD/YYY -> YYYY-MM-DD
    db[table].convert("Date", lambda val: parser.parse(val).date().isoformat())

    # impact of index is unclear, but seems wise
    db[table].create_index(["Date", "Utility"])


def get_connection(db: str) -> sqlite3.Connection:
    # return the right db
    return sqlite3.connect(db)
