import csv
import json
import re

REGEX = r': (.*) (?:->) (.*)'

# Goes through the complete CSV file (`complete.csv`) and extracts all the stations it encounters.
# This script creates a JSON file with all stations that occur in the CSV file without any duplicates.

# Load Infrabel's station list
stations = []
print('Opening ../spreadsheets/complete.csv')
with open('../spreadsheets/complete.csv', 'r') as f:
	reader = csv.reader(f)

	for row_index, row in enumerate(reader):
		print(f'\rProcessing row {row_index}', end='\r')
		stop = row[13].lower()  # Current stop
		if stop not in stations:
			stations.append(stop)
			print(f'Found new station: {stop}')

		if row[12] != '':  # If a direction field is given ==> extract departure and arrival station
			arrival = re.search(REGEX, row[12]).group(1).lower()
			departure = re.search(REGEX, row[12]).group(2).lower()
			if arrival not in stations:
				stations.append(arrival)
				print(f'Found new station: {arrival}')
			if departure not in stations:
				stations.append(departure)
				print(f'Found new station: {departure}')

with open('unique_stations.json', 'w') as f:
	json.dump(stations, f)
