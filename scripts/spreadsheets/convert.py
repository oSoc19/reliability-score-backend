#!/usr/bin/python3
import os
import sys
import errno

# Get all the Excel files from our `downloads` folder.
# These files are retrieved with the `crawler.py` script.
files = sorted(os.listdir('downloads'))

# Create a `csv` folder to store the output files.
try:
	os.mkdir('csv')
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

# Tested on Ubuntu 18.04 LTS (Linux).
# You need the install `csvkit` by running `pip3 install --user csvkit` in your terminal.
# Add the executable directory to your PATH variable: `export PATH=~/.local/bin:$PATH` in your terminal.
# You can run this script on multiple cores by running `python3 convert.py <START_INDEX> <INCREMENT>`.
# If you don't define these parameters, the script runs on a single core.
# START_INDEX = core number
# INCREMENT = the amount of available cores for this script
# For example, you want to run this on 3 cores, you run the following commands:
# `python3 convert.py 0 3 &`
# `python3 convert.py 1 3 &`
# `python3 convert.py 2 3 &`
# The ampersand makes the process running in the background, you can do other things while the converting takes place
start_index = 0
increment = 1
if len(sys.argv) == 3:
    start_index = int(sys.argv[1])
    increment = int(sys.argv[2])

for i in range(start_index, len(files), increment):
	file = files[i]
	print(f'Converting: {file}')

	xlsx_path = os.path.join('downloads', file)
	csv_path = os.path.join('csv', file[:-4]+'csv')
	command = f'in2csv {xlsx_path} > {csv_path}'

	os.system(command)

	print(f'Converted {file} {i+1}/{len(files)} ({(i+1)/len(files)*100}%)')
