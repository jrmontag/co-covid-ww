# App Runbook

Sometimes things go awry. Better to have troubleshooting and resolution steps written down.

## Data downloaded from portal is incomplete or corrupt

The new data downloads are typically ~4 MB on disk, comprising about 27,000 observations. If an incomplete new download gets inserted into the database:

1. verify the table is different than a recent one

```bash
sqlite-utils tables wastewater.db --table
sqlite-utils query wastewater.db "select count(*) from latest" --table
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

6. verify [the streamlit app](https://colorado-covid-wastewater.streamlit.app/) reloads correctly
