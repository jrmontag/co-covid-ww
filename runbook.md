# App Runbook

Sometimes things go awry. Better to have troubleshooting and resolution steps written down.

## Data downloaded from portal is incomplete or corrupt

The new data downloads are typically ~4 MB on disk, comprising about 27,000 observations. Sometimes, 
the open data portal returns a truncated (but still valid JSON) response with an additional 
`"exceededTransferLimit": true` entry. The 
[ArcGIS docs suggest](https://resources.arcgis.com/en/help/runtime-wpf/apiref/index.html?ESRI.ArcGIS.Client~ESRI.ArcGIS.Client.FeatureLayer~ExceededTransferLimit.html) 
that this is tripping some sort of max transfer size check. Unclear why it happens from time to 
time, but it does.

If an incomplete new download gets inserted into the database:

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

## Modify systemd service unit and reboot

If changing the service file:

1. `systemctl stop wastewater`
2. modify `wastewater.service` in repo
3. copy to `systemd` path as in `server_setup.sh`
4. run `systemctl daemon-reload`
5. `systemctl start wastewater`

