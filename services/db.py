from itertools import chain
import json
import logging
from pathlib import Path
import sqlite3
from typing import List, Optional, Tuple
from fastapi import Depends
from models.report import Report

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_connection(db_uri: str) -> sqlite3.Connection:
    # return the right db
    return sqlite3.connect(db_uri, check_same_thread=False)


def get_utilities(db: sqlite3.Connection):
    # CRUD: utilities
    query = "SELECT DISTINCT Utility FROM '2022-11-17' ORDER BY Utility ASC"
    list_of_lists: List[Tuple[str]] = db.execute(query).fetchall()
    result = list(chain.from_iterable(list_of_lists))
    return result


def get_samples(db: sqlite3.Connection, report: Report = Depends()):
    # CRUD: samples
    pass


def get_cases(db: sqlite3.Connection, report: Report = Depends()):
    # CRUD: cases
    pass