from datetime import date, timedelta
import sqlite3

from fastapi.testclient import TestClient

from main import app, configure_logging
from api.data_api import get_db_conn, API_ROOT

DEFAULT_UTILITY = "Metro WW - Platte/Central"

logger = configure_logging("dev")


# TODO: create an override + tests to verify the status=500 code paths where the conn is bad
def override_db_conn() -> sqlite3.Connection:
    """Use an in-memory db for API testing"""
    # load some test data into a db and table that match prod names
    # (note: TBD )
    test_cols = [
        "Date",
        "Utility",
        "SARS_COV_2_Copies_L_LP1",
        "SARS_COV_2_Copies_L_LP2",
        "Cases",
    ]

    # the default Report range is dynamically (-30d, today) - ensure that
    # the test data always includes something in that range
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    test_data = [
        ("2022-03-16", "Arapahoe County", 1, 0, 0),
        ("2022-03-17", "Arapahoe County", 3, 0, 0),
        ("2022-03-19", "Arapahoe County", 5, 0, 0),
        (yesterday, DEFAULT_UTILITY, 3, 0, 0),
        (today, DEFAULT_UTILITY, 9, 0, 0),
    ]

    test_table = "latest"
    table_cols = f"{test_table}({','.join(test_cols)})"
    table_create_stmt = f"CREATE TABLE {table_cols}"
    insert_stmt = f"INSERT INTO {table_cols} VALUES (?, ?, ?, ?, ?)"

    con: sqlite3.Connection = sqlite3.connect(":memory:")
    con.execute(table_create_stmt)
    con.executemany(insert_stmt, test_data)
    logger.debug("created and loaded test db")
    return con


app.dependency_overrides[get_db_conn] = override_db_conn
client = TestClient(app)


def test_home():
    resp = client.get("/")
    assert resp.status_code == 200

    test_content = "A Colorado COVID-19 Wastewater data API"
    assert test_content in resp.content.decode()


def test_utilities():
    resp = client.get(f"{API_ROOT}/utilities")
    assert resp.status_code == 200

    resp_json = resp.json()
    assert "utilities" in resp_json
    assert len(resp_json["utilities"]) == 2


def test_samples_default():
    resp = client.get(f"{API_ROOT}/samples")
    assert resp.status_code == 200

    resp_json = resp.json()
    assert all(x in resp_json for x in ["parameters", "samples"])
    assert resp_json["parameters"]["utility"] == DEFAULT_UTILITY
    assert len(resp_json["samples"]) == 2


def test_samples_start():
    start = "2022-12-01"
    query_path = f"{API_ROOT}/samples?start={start}"
    resp = client.get(query_path)

    resp_json = resp.json()
    assert all(x in resp_json for x in ["parameters", "samples"])
    assert resp_json["parameters"]["utility"] == DEFAULT_UTILITY
    assert resp_json["parameters"]["start"] == start
    assert resp_json["samples"][0][0] >= start
    assert len(resp_json["samples"]) == 2


def test_samples_end():
    end = "2050-12-01"
    query_path = f"{API_ROOT}/samples?end={end}"
    resp = client.get(query_path)

    resp_json = resp.json()
    assert all(x in resp_json for x in ["parameters", "samples"])
    assert resp_json["parameters"]["utility"] == DEFAULT_UTILITY
    assert resp_json["parameters"]["end"] == end
    assert resp_json["samples"][-1][0] <= end
    assert len(resp_json["samples"]) == 2


def test_samples_all():
    util = "Arapahoe County"
    start = "2022-03-01"
    end = "2022-03-20"
    query_path = f"{API_ROOT}/samples?utility={util}&start={start}&end={end}"
    resp = client.get(query_path)

    resp_json = resp.json()
    assert all(x in resp_json for x in ["parameters", "samples"])
    assert resp_json["parameters"]["utility"] == util
    assert resp_json["parameters"]["start"] >= start
    assert resp_json["parameters"]["end"] <= end
    assert resp_json["samples"][0][0] >= start
    assert resp_json["samples"][-1][0] <= end
    assert len(resp_json["samples"]) == 3
