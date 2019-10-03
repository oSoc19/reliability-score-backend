#!/usr/bin/python3

import csv
import requests
import re
import os
import errno

# Create downloads folder if needed
try:
    os.makedirs('downloads')
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

# Download Excel file one-by-one
with open('list_spreadsheets.csv', 'r', newline='') as f:
	reader = csv.reader(f, delimiter=';')
	urls = []
	for row in reader:
		urls.append(row[1])


	start = 0
	for i in range(start, len(urls)):
		url = urls[i]
		filename = re.search('Raw_.*', url).group(0)

		r = requests.get(url, stream=True)

		with open(f'downloads/{filename}', 'wb') as f:
			f.write(r.content)

		progress = i + 1
		total = len(urls)
		print(f'Downloaded {filename} ({progress}/{total})')
