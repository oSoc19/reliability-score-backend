import csv
import json
import re
from fuzzywuzzy import process


station_uris = {}

# Load Infrabel's station list
with open('unique_stations.json') as f:
	stations = json.load(f)


# Load iRail's station to URI csv
csv_uris = {}
with open('stations.csv', 'r') as f:
	reader = csv.reader(f)
	for row in reader:
		uri = row[0]
		station = row[1].lower()
		if station not in csv_uris:
			csv_uris[station] = uri


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