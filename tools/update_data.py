import argparse
from csv import DictReader
from datetime import date, datetime, timedelta
import json
import logging
from pathlib import Path
from typing import List, Optional
from dateutil import parser as date_parser
import requests
from sqlite_utils import Database


parser = argparse.ArgumentParser()
parser.add_argument("--csv", help="filepath to csv data file")
parser.add_argument("--json", help="filepath to json data file")
args = parser.parse_args()

# dataset landing page > View Table > More info >
# I want to use this... > View Data Source
PORTAL_URL_ROOT = (
    "https://services3.arcgis.com/66aUo8zsujfVXRIT/arcgis/rest/services"
    + "/CDPHE_COVID19_Wastewater_Data/FeatureServer/1"
)

# see docstring for fetch_portal_data
PARTIAL_UPDATE_THRESHOLD = 45_000


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
    level=logging.DEBUG,
)


def get_latest_local_update() -> Optional[date]:
    """Return the date associated with the local file version of the data"""
    logger.debug("Checking for latest local update")
    # assumes cwd = repo root
    data_dir = Path.cwd() / "data"
    # file name convention: 2022-11-18_download.(json|csv)
    # must match naming convention in fetch fn!
    present_json = list(Path(data_dir).glob("*_download.json"))
    present_csv = list(Path(data_dir).glob("*_download.csv"))
    present_data = present_json + present_csv
    if len(present_data) == 0:
        logger.warning(f"Found no local data files in {Path(data_dir)}")
        return None
    else:
        latest_data_file = sorted(present_data, reverse=True)[0].parts[-1]
        latest_date = latest_data_file.split("_")[0]
        logger.debug(f"Latest local file date: {latest_date}")
        result = date_parser.parse(latest_date).date()
        return result


def get_latest_portal_update() -> date:
    """Return the latest update date according to the portal metadata API"""
    # ref: https://services3.arcgis.com/66aUo8zsujfVXRIT/arcgis/rest/services/
    # CDPHE_COVID19_Wastewater_Dashboard_Data/FeatureServer/0
    # fetch portal data metadata json
    logger.debug("Checking for latest update date from portal metadata")
    query = PORTAL_URL_ROOT + "?f=pjson"
    data = requests.get(query).json()
    if data.get("error"):
        raise Exception(f"Error fetching portal metadata. Response: {data}")
    update_epoch_ms = data["editingInfo"]["dataLastEditDate"]
    update = date.fromtimestamp(update_epoch_ms / 1000.0)
    logger.debug(f"Latest reported portal data edit date (epoch ms): {update} ({update_epoch_ms})")
    return update


def fetch_portal_json_data(last_update: datetime) -> dict:
    """Return (and serialize) the current data available through the portal API"""
    logger.debug(f"Fetching new data from portal")
    # "fun" quirks:
    # - the state's API has a max record count response of 32000 ObjectIds
    # split into multiple requests of chunk_size
    # currently ~48k object ids, grows a few hundred with each update
    # set PARTIAL_UPDATE_THRESHOLD accordingly
    # refs:
    # https://services3.arcgis.com/66aUo8zsujfVXRIT/arcgis/rest/services/
    # CDPHE_COVID19_Wastewater_Dashboard_Data/FeatureServer/0
    # https://developers.arcgis.com/rest/services-reference/
    # enterprise/query-feature-service-layer-.htm
    # - quite often (for unknown reasons) the state's API will return a valid
    # json response with only a subset of the available data and no other
    # indication of an error. save this partial data with a different pattern
    # and log it. anecdotally, this situation returns ~20k records.
    chunk_size = 5_000
    results_cap = 80_000
    result = dict()
    offsets = (i * chunk_size for i in range(results_cap // chunk_size))
    for offset in offsets:
        logger.debug(f"API request params: {offset=}, {chunk_size=}")
        query = (
            PORTAL_URL_ROOT
            + "/query?where=1%3D1&outFields=*&outSR=4326&f=json&"
            + f"resultOffset={offset}&resultRecordCount={chunk_size}"
        )
        response = requests.get(query).json()
        if existing_features := result.get("features"):
            existing_features.extend(response["features"])
        else:
            result = response
        # short-circuit the loop if we've passed beyond the available record count
        # (the api will return empty array)
        if len(response["features"]) == 0:
            break
    results_size = len(result.get("features", []))
    logger.debug(f"Total object count: {results_size}")

    # side-effect saving latest data
    last_update_date = last_update.strftime("%Y-%m-%d")
    if results_size > PARTIAL_UPDATE_THRESHOLD:
        new_local_data = f"data/{last_update_date}_download.json"
    else:
        # "-partial" convention will prevent data from matching in get_latest_local_update
        new_local_data = f"data/{last_update_date}_download-partial.json"
    Path(new_local_data).write_text(json.dumps(result))
    logger.info(f"Wrote backup of fetched data to {new_local_data}")
    return result


def transform_raw_json_data(raw_data: dict) -> List[dict]:
    """Convert the downloaded JSON data to the format compatible with bulk loading in DB"""
    logger.debug("Transforming raw data to preferred schema")
    try:
        features: List[dict] = raw_data["features"]
    except KeyError as ke:
        raise Exception(
            f"Input data did not match expected schema. Observed keys: {raw_data.keys()}"
        )
    if raw_data.get("exceededTransferLimit"):
        logger.debug("ArcGiS transfer limit exceeded; results may be truncated")
    flat_features: List[dict] = []
    for i, feature in enumerate(features):
        flat_feature: dict = feature["attributes"]
        del flat_feature["OBJECTID"]
        flat_features.append(flat_feature)
    logger.info(f"Counted {i} observations during data transformation")
    return flat_features


def update_db_from_json_file(data_file: str) -> None:
    """Manually run a db update from a local JSON download"""
    logger.info(f"Initiating database update from local JSON: {data_file}")
    raw_data = json.loads(Path(data_file).read_text())
    xformed_data = transform_raw_json_data(raw_data)
    tmp_date = (date.today() - timedelta(days=1)).isoformat()
    update_db(data=xformed_data, latest_local=tmp_date)


def fetch_portal_csv_data() -> str | None:
    logging.info("Attempting to fetch CSV data from portal")
    # from dev tools network inspection of download page
    url = (
        "https://opendata.arcgis.com/api/v3/datasets"
        "/2d227e6c65f0450cb39759612cda5e9e_1/downloads"
        "/data?format=csv&spatialRefId=4326&where=1=1"
    )
    response = requests.get(url)
    if response.status_code == 200:
        filepath = f"data/{date.today().isoformat()}_download.csv"
        logging.debug(f"Writing fetched data to {filepath}")
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filepath
    else:
        return None


# TODO: consistent date transformations upstream of update_db (remove)
def transform_raw_csv_data(csv_row: dict) -> dict:
    """Adjust the dict to match the expected schema defined in update_db."""
    # date string -> epoch ms
    # upstream format doesn't match a python formatter without slight mod
    raw_dt = csv_row["Date"]
    mod_dt = raw_dt + "00"
    input_format = "%Y/%m/%d %H:%M:%S%z"
    dt = datetime.strptime(mod_dt, input_format)
    epoch_ms = int(dt.timestamp() * 1000.0)
    csv_row["Date"] = epoch_ms
    # drop unused field
    del csv_row["OBJECTID"]
    # cast numeric vals (match schema in update_db)
    for k in ["SARS_COV_2_Copies_L_LP1", "SARS_COV_2_Copies_L_LP2"]:
        try:
            csv_row[k] = float(csv_row[k])
        except ValueError:
            csv_row[k] = None
    csv_row["Cases"] = int(csv_row["Cases"])
    return csv_row


def update_db_from_csv_file(data_file: str) -> None:
    """Manually run a db update from a local CSV download"""
    logger.info(f"Initiating database update from local csv: {data_file}")
    # read csv with stdlib csv module
    xformed_data = []
    with open(data_file, encoding="utf-8-sig", mode="r") as f:
        reader = DictReader(f)
        for row in reader:
            xformed_data.append(transform_raw_csv_data(row))
    tmp_date = (date.today() - timedelta(days=1)).isoformat()
    update_db(data=xformed_data, latest_local=tmp_date)


def update_db(data: List[dict], latest_local: Optional[str]) -> None:
    """Update the db to reflect the latest data, including making a backup table"""
    logger.debug("Updating local database")
    database = "data/wastewater.db"
    main_table = "latest"
    db = Database(database)
    if latest_local and (main_table in db.table_names()):
        logger.debug(f"Moving {database}[{main_table}] to {database}[{latest_local}]")
        # move existing content to backup table named by download date
        db.execute(f"ALTER TABLE `{main_table}` RENAME TO `{latest_local}`")

    logger.info(f"Creating and inserting new data to {database=} {main_table=}")
    # sqlite-utils incorrectly auto-infers a measurement col as string, so set schema manually
    db[main_table].create(
        {
            "Date": int,
            "Utility": str,
            "SARS_COV_2_Copies_L_LP1": float,
            "SARS_COV_2_Copies_L_LP2": float,
            "Cases": int,
            "Lab_Phase": str,
        }
    )
    db[main_table].insert_all(records=data)

    logger.debug(f"Transforming date to ISO format in {database=} {main_table=}")
    # epoch -> YYYY-MM-DD
    db[main_table].convert("Date", lambda x: datetime.fromtimestamp(x / 1000.0).date().isoformat())
    names = db.table_names()
    logger.info(f"Table names in current db: {names}")


if __name__ == "__main__":
    if args.csv:
        update_db_from_csv_file(args.csv)
    elif args.json:
        update_db_from_json_file(args.json)
    else:
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
            latest_data = fetch_portal_json_data(latest_portal_update)
            transformed_data = transform_raw_json_data(latest_data)
            # don't update the DB with partial data - the front-end ux is bad
            # see docstring for fetch_portal_data
            if len(transformed_data) > PARTIAL_UPDATE_THRESHOLD:
                update_db(data=transformed_data, latest_local=local_date)
            else:
                logger.info("Fetched + transformed data is unusually small - skipping update.")
                # try csv update
                if csv_file := fetch_portal_csv_data():
                    update_db_from_csv_file(csv_file)
                    logging.info("Updated DB from CSV import")
                else:
                    logger.info("CSV portal fetch unsuccessful")
        else:
            logger.info(f"Not updating local data files")
    logger.info("Completed run of data check/fetch")
