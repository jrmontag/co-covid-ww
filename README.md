# mobile-friendly CO wastewater data

the state has [an arcgis dashboard](https://cdphe.maps.arcgis.com/apps/dashboards/d79cf93c3938470ca4bcc4823328946b) that's pretty sweet if you have a giant display. maybe we can make something a little more mobile-friendly.

```
(venv) ~/code/co-covid-ww 
$ python -i main.py 
done!
>>> import db
>>> conn = db.get_connection('wastewater.db')
>>> for row in conn.execute("select * from '2022-11-17' where Utility = 'Boulder' order by Date desc limit 5"):
...  print(row)
... 
('2022-11-14', 'Boulder', None, 0)
('2022-11-13', 'Boulder', None, 10)
('2022-11-12', 'Boulder', None, 13)
('2022-11-11', 'Boulder', None, 19)
('2022-11-10', 'Boulder', 408918.0, 22)
```