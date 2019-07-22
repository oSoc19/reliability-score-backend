import csv
import requests
import re


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