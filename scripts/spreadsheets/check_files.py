import csv
import re
import os


with open('list_spreadsheets.csv', 'r', newline='') as f:
	reader = csv.reader(f, delimiter=';')
	urls = []
	for row in reader:
		urls.append(row[1])


for url in urls:
	filename = re.search('Raw_.*', url).group(0)[:-4] + 'csv'
	if not os.path.exists(f'csv/{filename}'):
		print(filename)
