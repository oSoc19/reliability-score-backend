#!/usr/bin/python3

import csv
import json
import re
import requests
import os.path
from fuzzywuzzy import process
IRAIL_CSV_URL='https://raw.githubusercontent.com/iRail/stations/master/stations.csv'

station_uris = {}

# Load Infrabel's station list
with open('unique_stations.json') as f:
	stations = json.load(f)
print('Reading unique_stations.json OK')

# Load iRail's station to URI csv
if not os.path.isfile('stations.csv'):
	r = requests.get(IRAIL_CSV_URL, stream=True)
	with open('stations.csv', 'wb') as f:
		f.write(r.content)
	print('iRail stations.csv download OK')

csv_uris = {}
with open('stations.csv', 'r') as f:
	reader = csv.reader(f)
	for row in reader:
		uri = row[0]
		station = row[1].lower()
		if station not in csv_uris:
			csv_uris[station] = uri
print('iRail stations.csv reading OK')

print('Matching stations... Incomplete stations might require user interaction to match them properly')
for station in stations:
	if station in csv_uris:
		station_uris[station] = csv_uris[station]
	else:  # Infrabel station not found in iRail list ==> fuzzy search for similar stations and select manually
		guesses = process.extract(station, csv_uris.keys())
		print(station)
		for i in range(len(guesses)):
			print(f'[{i}] {guesses[i]}')
		choice = input('Choice: ')
		if choice == '':
			continue  # Skip this station (for duplicate stations)
		else:
			station_uris[station] = csv_uris[guesses[int(choice)][0]]


with open('station_to_uri.json', 'w') as f:
	json.dump(station_uris, f)
print('Generating station_to_uri.json OK')
