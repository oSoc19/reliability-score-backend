# Stations to URIs

`unique_stations.py` takes the Infrabel dataset as input and outputs a list of all the unique stations to `unique_stations.json`.

`station_to_uri.py` takes `unique_stations.json` and the iRail stations CSV as input and tries to match as many stations as possible. It then performs a fuzzy search for the stations it couldn't find and gives suggestions the user can select them manually.