#!/usr/bin/env bash

# script to help accelerate development speed
# most of these commands have been moved into db.prepare_db

source venv/bin/activate

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- dropping table"
sqlite-utils drop-table wastewater.db 2022-11-17 --ignore

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- loading data"
sqlite-utils insert wastewater.db 2022-11-17 2022-11-17_ww.flat.json

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- data preview:"
sqlite-utils query wastewater.db "select * from '2022-11-17' limit 5" --table

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- reformatting dates"
sqlite-utils convert wastewater.db 2022-11-17 Date 'r.parsedate(value)'

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- adding table indexes"
sqlite-utils create-index wastewater.db '2022-11-17' Date Utility

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- data preview:"
sqlite-utils query wastewater.db "select * from '2022-11-17' limit 5" --table

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- table schema:"
sqlite-utils tables wastewater.db --schema --table

echo "$(date +%Y-%m-%d\ %H:%M:%S) -- current indexes:"
sqlite-utils indexes wastewater.db --table
