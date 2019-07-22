import os
import sys


files = os.listdir('downloads')
start = sys.argv[1]
cores = 4


for i in range(start, len(files), cores):
	file = files[i]

	xlsx_path = os.path.join('downloads', file)
	csv_path = os.path.join('csv', file[:-4]+'csv')
	command = f'in2csv {xlsx_path} > {csv_path}'

	os.system(command)

	print(f'Converted {file} {i+1}/{len(files)} ({(i+1)/len(files)*100}%)')