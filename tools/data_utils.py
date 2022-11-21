import json
import logging
from pathlib import Path
from typing import List, Optional
from dateutil import parser
from sqlite_utils import Database


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def fetch_data():
    # CDPHE portal data
    # https://data-cdphe.opendata.arcgis.com/datasets/CDPHE::cdphe-covid19-wastewater-dashboard-data/about
    query = (
        "https://services3.arcgis.com/66aUo8zsujfVXRIT/arcgis/rest/services/"
        + "CDPHE_COVID19_WW_Dashboard_Data_Publish/FeatureServer/0/query?"
        + "where=1%3D1&outFields=*&outSR=4326&f=json"
    )
    # write "2022-11-17_download.json" or similar
    pass


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
    # TODO: move existing `latest` to dated table
    db[table].insert_all(records=table_data, truncate=truncate)

    # MM/DD/YYY -> YYYY-MM-DD
    db[table].convert("Date", lambda val: parser.parse(val).date().isoformat())

    # impact of index is unclear, but seems wise
    db[table].create_index(["Date", "Utility"])


def load_and_prep_db():
    # lots of hard-coded constants for now
    data_dir = "data"
    in_file = f"{data_dir}/2022-11-17_download.json"
    out_file = f"{data_dir}/2022-11-17_latest.json"
    process_raw_data(in_file, out_file)

    sql_db = f"{data_dir}/wastewater.db"
    table = "latest"
    truncate = True
    prepare_db(sql_db, table, out_file, truncate)

    logger.debug("completed db setup")
