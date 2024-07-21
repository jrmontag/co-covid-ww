from itertools import chain
import logging
import sqlite3
from typing import List, Tuple
from fastapi import Depends

from models.observation import CdpheObservation
from models.report import Report

logger = logging.getLogger(__name__)

# DB conventions
PROD_TABLE = "latest"
DATE_COL = CdpheObservation.DATE.value
SAMPLES_COLS = [CdpheObservation.COPIES_LP2.value, CdpheObservation.COPIES_LP1.value]
UTILITY_COL = CdpheObservation.UTILITY.value


def get_connection(db_uri: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_uri, check_same_thread=False)
    # metadata table that includes tables and indexs in the db
    entities = conn.execute("SELECT * FROM sqlite_master").fetchall()
    if len(entities) == 0:
        logger.error("Database is present but empty!")
    return conn


def get_utilities(conn: sqlite3.Connection) -> List[str]:
    # CRUD fn for utilities
    query = (
        f"SELECT DISTINCT {UTILITY_COL} " + f"FROM {PROD_TABLE} " + f"ORDER BY {UTILITY_COL} ASC"
    )
    logger.debug(f"Issuing db query: {query}")
    list_of_utility_lists: List[Tuple[str]] = conn.execute(query).fetchall()
    # flatten lists
    result = list(chain.from_iterable(list_of_utility_lists))
    return result


def get_samples(conn: sqlite3.Connection, report: Report = Depends()) -> List[str]:
    # CRUD fn for samples
    # notes on sqlite quoting and keywords: https://www.sqlite.org/lang_keywords.html
    cols = f"{DATE_COL}, {','.join(SAMPLES_COLS)}"
    condition = (
        f"{UTILITY_COL} = '{report.utility}' "
        + f"AND {DATE_COL} >= '{report.start}' "
        + f"AND {DATE_COL} <= '{report.end}'"
    )
    query = (
        f"SELECT {cols} "
        + f"FROM {PROD_TABLE} "
        + f"WHERE {condition} "
        + f"ORDER BY {DATE_COL} ASC"
    )
    logger.debug(f"Issuing db query: {query}")
    result = conn.execute(query).fetchall()
    return result


def get_cases(db: sqlite3.Connection, report: Report = Depends()):
    # CRUD: cases
    pass
