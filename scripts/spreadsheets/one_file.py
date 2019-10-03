#!/usr/bin/python3
import os

# Combine all the CSV files into a single CSV file 'complete.csv'
outfile = 'complete.csv'

# Read the `csv` folder
files = os.listdir('csv')

# Open every CSV file, read it and add it to our `complete.csv` file
with open(outfile, 'w') as outfile:
	for i in range(0, len(files)):
		infile = os.path.join('csv', files[i])
		with open(infile, 'r') as infile:
			# Remove the heading of the individual CSV files before writing
			text = infile.read().replace('DATDEP,TRAIN_NO,RELATION,TRAIN_SERV,PTCAR_NO,LINE_NO_DEP,REAL_TIME_ARR,REAL_TIME_DEP,PLANNED_TIME_ARR,PLANNED_TIME_DEP,DELAY_ARR,DELAY_DEP,RELATION_DIRECTION,PTCAR_LG_NM_NL,LINE_NO_ARR,PLANNED_DATE_ARR,PLANNED_DATE_DEP,REAL_DATE_ARR,REAL_DATE_DEP\n', '')
			outfile.write(text)
		print(f'{i+1}/{len(files)} ({(i+1)/len(files)*100}%)')
