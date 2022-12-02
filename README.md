# Queryable CO wastewater data

The state has [an arcgis dashboard](https://cdphe.maps.arcgis.com/apps/dashboards/d79cf93c3938470ca4bcc4823328946b) that's pretty sweet if you have a computer. It is also a bit heavy-handed and very unfriendly to mobile users. 

This application creates queryable API for this data at `http://wastewater.jrmontag.xyz` that updates shortly after the official data is updated.

There is basic API documentation [available here](http://wastewater.jrmontag.xyz/docs/).

A mobile-friendly Streamlit frontend for this API [can be found here](https://colorado-covid-wastewater.streamlit.app/).


This application is made possible thanks to the lovely Colorado state [Open Data Portal](https://data-cdphe.opendata.arcgis.com/datasets/CDPHE::cdphe-covid19-wastewater-dashboard-data/about).


# FAQ

**Isn't this application a bit over-engineered given that the data from the portal is a few MB in size?**

Yes, it totally is. You could fetch the entire timeseries each time and hold it in memory for whatever data display applications you had in mind. This application wasn't designed to be maximally efficient! It was intended as a learning opportunity to create something real and online using some recent frameworks and libraries like FastAPI and Streamlit. 


