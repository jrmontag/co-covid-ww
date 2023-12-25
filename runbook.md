# App Runbook

Sometimes things go awry. Better to have troubleshooting and resolution steps written down.

## Manually update data from JSON API

The new data downloads are typically ~13 MB JSON on disk, comprising about 50k observations. Sometimes, 
the open data portal returns a truncated (but still valid JSON) response with an additional 
`"exceededTransferLimit": true` entry. The 
[ArcGIS docs suggest](https://resources.arcgis.com/en/help/runtime-wpf/apiref/index.html?ESRI.ArcGIS.Client~ESRI.ArcGIS.Client.FeatureLayer~ExceededTransferLimit.html) 
that this is tripping some sort of max transfer size check. Unclear why it happens from time to 
time, but it does.

The general approach for this app is to upload the entire (new) dataset to a new `latest` table each time, 
moving the previous version to a dated table.

If an incomplete new download gets inserted into the database:

1. verify the table is different than a recent one

```bash
sqlite-utils tables wastewater.db --table
sqlite-utils query wastewater.db "select count(*) from latest" --table
sqlite-utils query wastewater.db "select * from latest where SARS_COV_2_Copies_L_LP2 is not NULL order by Date desc limit 10" --table
sqlite-utils query wastewater.db "select count(*) from '2022-12-05'" --table
```

2. (optional) inspect the most recent download in a REPL 

```python
d = tools.update_data.fetch_portal_data(datetime.utcnow())
```

3. remove the most recent download file from the app's local `data/` directory

4. drop the `latest` table from the db

```bash
sqlite-utils tables wastewater.db --table
sqlite-utils drop-table wastewater.db latest
sqlite-utils tables wastewater.db --table
```

5. manually run a data update 

```bash
python tools/update_data.py
```

or 

copy the contents of a previous table into `latest`

```bash
sqlite-utils duplicate wastewater.db 2023-11-09 latest
```

6. inspect relevant data table

```bash
sqlite-utils query wastewater.db "select * from 'latest' where Utility like '%Central%' order by Date desc limit 15" --table
```

7. verify [the streamlit app](https://colorado-covid-wastewater.streamlit.app/) reloads correctly


## Manually update data from CSV download

CDPHE API returns JSON, but sometimes the API is just stubborn and won't return all the data for weeks on end. Or maybe they changed the way the API works. Who knows. Regardless the available CSV download seems updated, however some of the data fields are in different formats because why not.

1. download csv from cdphe
2. point update_data.py to csv (or use upload method from repl) 
``$ python tools/update_data.py --csv data/2023-12-23_download.csv``



## Walk through `__main__` steps manually

From a fresh ipython repl in the venv
```python
from tools.update_data import *
from sqlite_utils.utils import sqlite3
from datetime import datetime
from dateutil import parser
from pathlib import Path

sqlite3.enable_callback_tracebacks(True)
latest_local_update = parser.parse('2023-09-09').date()
latest_portal_update = get_latest_portal_update()
download = 'data/2023-09-11_download.json'
raw_data = json.loads(Path(download).read_text())
xformed_data = transform_raw_data(raw_data)
database = "data/wastewater.db"
main_table = "latest"
db = Database(database)
db[main_table].insert_all(records=xformed_data)
```

## Modify systemd service unit and reboot

If changing the service file:

1. `systemctl stop wastewater`
2. modify `wastewater.service` in repo
3. copy to `systemd` path as in `server_setup.sh`
4. run `systemctl daemon-reload`
5. `systemctl start wastewater`

