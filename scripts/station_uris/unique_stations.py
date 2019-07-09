import csv
import json
import re


REGEX = r': (.*) (?:->) (.*)'


# Load Infrabel's station list
stations = []
with open('../../data/dataset.csv', 'r') as f:
	reader = csv.reader(f)
	for row in reader:
		stop = row[13].lower()  # Current stop
		if stop not in stations:
			stations.append(stop)

		if row[12] != '':  # If a direction field is given ==> extract departure and arrival station
			arrival = re.search(REGEX, row[12]).group(1).lower()
			departure = re.search(REGEX, row[12]).group(2).lower()
			if arrival not in stations:
				stations.append(arrival)
			if departure not in stations:
				stations.append(departure)


with open('unique_stations.json', 'w') as f:
	json.dump(stations, f)


print(stations)