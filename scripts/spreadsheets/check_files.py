!#/usr/bin/python3
import csv
import re
import os

# Check the list of spreadsheets we should have now on your system
with open('list_spreadsheets.csv', 'r', newline='') as f:
	reader = csv.reader(f, delimiter=';')
	urls = []
	for row in reader:
		urls.append(row[1])

# Print every file which has not been succesfully converted to CSV
for url in urls:
	filename = re.search('Raw_.*', url).group(0)[:-4] + 'csv'
	if not os.path.exists(f'csv/{filename}'):
		print(filename)
