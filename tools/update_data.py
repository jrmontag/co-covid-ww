from datetime import date, datetime, timedelta
import json
import logging
from pathlib import Path
from typing import List, Optional
from dateutil import parser
import requests
from sqlite_utils import Database


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


def get_latest_local_update() -> Optional[date]:
    """Return the date associated with the local file version of the data"""
    logger.debug("Checking for latest local update")
    # assumes cwd = repo root
    data_dir = Path.cwd() / "data"
    # must match naming convention in fetch fn
    latest_data = list(Path(data_dir).glob("*_download.json"))
    if len(latest_data) == 0:
        logger.warning(f"Found no local data files in {Path(data_dir)}")
        return None
    else:
        # file name convention: 2022-11-18_download.json
        latest_data_file = sorted(latest_data, reverse=True)[0].parts[-1]
        latest_date = latest_data_file.split("_")[0]
        logger.debug(f"Latest local file date: {latest_date}")
        result = parser.parse(latest_date).date()
        return result


def get_latest_portal_update() -> date:
    """Return the latest update date according to the portal metadata API"""
    # fetch portal data metadata json
    logger.debug("Checking for latest update date from portal metadata")
    query = (
        "https://services3.arcgis.com/66aUo8zsujfVXRIT/arcgis/rest/services"
        + "/CDPHE_COVID19_WW_Dashboard_Data_Publish/FeatureServer/0?f=pjson"
    )
    data = requests.get(query).json()
    update_epoch_ms = data["editingInfo"]["dataLastEditDate"]
    update = date.fromtimestamp(update_epoch_ms / 1000.0)
    logger.debug(
        f"Latest reported portal data edit date (epoch ms): {update} ({update_epoch_ms})"
    )
    return update


def fetch_portal_data(last_update: datetime) -> dict:
    """Return (and serialize) the current data available through the portal API"""
    # fetch portal data json; write locally and return
    # https://data-cdphe.opendata.arcgis.com/datasets/CDPHE::cdphe-covid19-wastewater-dashboard-data/about
    logger.debug(f"Fetching new data from portal")
    query = (
        "https://services3.arcgis.com/66aUo8zsujfVXRIT/arcgis/rest/services"
        + "/CDPHE_COVID19_WW_Dashboard_Data_Publish/FeatureServer/0/query"
        + "?where=1%3D1&outFields=*&outSR=4326&f=json"
    )
    data = requests.get(query).json()
    last_update_date = last_update.strftime("%Y-%m-%d")
    new_local_data = f"data/{last_update_date}_download.json"
    Path(new_local_data).write_text(json.dumps(data))
    logger.info(f"Wrote backup of fetched data to {new_local_data}")
    return data


def transform_raw_data(raw_data: dict) -> List[dict]:
    """Convert the downloaded data to the format compatible with bulk loading in DB"""
    logger.debug("Transforming raw data to preferred schema")
    try:
        features: List[dict] = raw_data["features"]
    except KeyError as ke:
        raise Exception(
            f"Input data did not match expected schema. Observed keys: {raw_data.keys()}"
        )
    flat_features: List[dict] = []
    for i, feature in enumerate(features):
        flat_feature: dict = feature["attributes"]
        del flat_feature["ObjectId"]
        flat_features.append(flat_feature)
    logger.info(f"Counted {i} observations during data transformation")
    return flat_features


def update_db(data: List[dict], latest_local: Optional[str]) -> None:
    """Update the db to reflect the latest data, including making a backup table"""
    logger.debug("Updating local database")
    database = "data/wastewater.db"
    main_table = "latest"
    db = Database(database)
    if latest_local and (main_table in db.table_names()):
        logger.debug(f"Moving {database}.{main_table} to {database}.{latest_local}")
        # move existing content to backup table named by download date
        db.execute(f"ALTER TABLE `{main_table}` RENAME TO `{latest_local}`")

    logger.info(f"Inserting new data to {database=} {main_table=}")
    db[main_table].insert_all(records=data)

    logger.debug(f"Transforming date to ISO format in {database=} {main_table=}")
    # MM/DD/YYY -> YYYY-MM-DD
    db[main_table].convert("Date", lambda val: parser.parse(val).date().isoformat())

    # verify
    names = db.table_names()
    logger.info(f"Table names in current db: {names}")


def update_db_from_file(download: str) -> None:
    """Manually run a db update from a local download"""
    logger.info(f"Initiating database update from local file: {download}")
    raw_data = json.loads(Path(download).read_text())
    xformed_data = transform_raw_data(raw_data)
    tmp_date = (date.today() - timedelta(days=1)).isoformat()
    update_db(data=xformed_data, latest_local=tmp_date)


if __name__ == "__main__":
    logger.info("> Starting new run of data check/fetch")
    latest_local_update: Optional[date] = get_latest_local_update()
    latest_portal_update: date = get_latest_portal_update()

    # simpler logs
    local_date = latest_local_update.isoformat() if latest_local_update else None
    portal_date = latest_portal_update.isoformat()
    comparison = f"portal date (local date): {portal_date} ({local_date})"
    logger.info(f"Observed latest updates -> {comparison}")

    if (not latest_local_update) or (latest_portal_update > latest_local_update):
        logger.info("Initiating data update")
        # download new json
        latest_data = fetch_portal_data(latest_portal_update)
        # adjust json content for db load
        transformed_data = transform_raw_data(latest_data)
        # update any existing db table, load new data
        update_db(data=transformed_data, latest_local=local_date)
    else:
        logger.info(f"Not updating local data files")

    logger.info("Completed run of data check/fetch")
