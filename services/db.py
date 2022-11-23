from itertools import chain
import json
import logging
from pathlib import Path
import sqlite3
from typing import List, Optional, Tuple
from fastapi import Depends
from models.report import Report

logger = logging.getLogger(__name__)

# DB conventions
PROD_TABLE = "latest"
DATE_COL = "Date"
SAMPLES_COL = "SARS_CoV_2_copies_L"
UTILITY_COL = "Utility"


def get_connection(db_uri: str) -> Optional[sqlite3.Connection]:
    conn = sqlite3.connect(db_uri, check_same_thread=False)
    # tables and indexs in the given db
    entities = conn.execute("SELECT * FROM sqlite_master").fetchall()
    if len(entities) == 0:
        logger.warning("Database is present but empty")
        conn = None
    return conn


def get_utilities(db: sqlite3.Connection) -> List[str]:
    # CRUD fn for utilities

    query = (
        f"SELECT DISTINCT {UTILITY_COL} "
        + f"FROM {PROD_TABLE} "
        + f"ORDER BY {UTILITY_COL} ASC"
    )
    logger.debug(f"Issuing db query: {query}")
    list_of_utility_lists: List[Tuple[str]] = db.execute(query).fetchall()
    logger.debug(f"Issued db query: {query}")
    # flatten lists
    result = list(chain.from_iterable(list_of_utility_lists))
    return result


def get_samples(db: sqlite3.Connection, report: Report = Depends()) -> List[str]:
    # CRUD fn for samples
    # notes on sqlite quoting and keywords: https://www.sqlite.org/lang_keywords.html
    cols = f"{DATE_COL}, {SAMPLES_COL}"
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
    result = db.execute(query).fetchall()
    return result


def get_cases(db: sqlite3.Connection, report: Report = Depends()):
    # CRUD: cases
    pass
