import pandas as pd
import numpy as np
import json
import re
import requests
import time
from datetime import datetime
from catboost import CatBoostRegressor, Pool


before = time.time()
cat = CatBoostRegressor()
cat.load_model('test_model.cbm')
after = time.time()
print(f'Loading model: {after-before} sec.')


stations_df = pd.read_csv('../data/stations.csv')
station_uris = json.load(open('../data/station_uris_irail.json', 'r'))




def station_to_uri(station):
	print(station)
	try:
		return station_uris[station]
	except KeyError:
		return None


def get_seconds_since_midnight(datetime):
	midnight =  datetime.replace(hour=0, minute=0, second=0, microsecond=0)
	return (datetime - midnight).total_seconds()


def get_line_number(vehicle):
	# Expected input: "IC1515"
	pattern = re.compile("^([A-Z]+)([0-9])+$")
	vehicle_type = pattern.match(vehicle).group(1)
	vehicle_nr = int(pattern.match(vehicle).group(2))
	line_nr = 0
	if vehicle_type == 'IC':
		line_nr = str(int(100 * np.floor(vehicle_nr / 100)))
	elif vehicle_type == 'L':
		line_nr = str(int(50 * np.floor(vehicle_nr / 50)))
	elif vehicle_type == 'S':
		line_nr = str(int(50 * np.floor(vehicle_nr / 50)))
	else:
		line_nr = 'P'
	return vehicle_nr, line_nr




def get_features(vehicle_id, time_str):
	parsed_time = pd.to_datetime(time_str, format='%d-%m-%Y %H:%M')
	parsed_time_str = parsed_time.strftime('%d%m%y')
	VEHICLE_URL = 'http://api.irail.be/vehicle/?id={}&date={}&format=json&lang=nl'.format(vehicle_id, parsed_time_str)

	train_type = vehicle_id.split('.')[-1]
	pattern = re.compile("^([A-Z]+)([0-9]+)$")
	vehicle_type = pattern.match(train_type).group(1)
	line_id = pattern.match(train_type).group(2)
	vehicle_nr, line = get_line_number(train_type)

	resp = requests.get(VEHICLE_URL)
	resp = json.loads(resp.content)
	dep_uri = resp['stops']['stop'][0]['stationinfo']['@id']  # Name of the departure station
	stop_dep = int(stations_df[stations_df['URI'] == dep_uri].iloc[0, :]['avg_stop_times'])
	arr_uri = resp['stops']['stop'][-1]['stationinfo']['@id']
	stop_arr = int(stations_df[stations_df['URI'] == arr_uri].iloc[0, :]['avg_stop_times'])

	delays = []
	for stop in resp['stops']['stop']:
		try:
			station_cur_uri = station_to_uri(stop['station'])
			station_cur = station_cur_uri.split('/')[-1]
			date = datetime.utcfromtimestamp(int(stop['time']))
			departure_time  = datetime.utcfromtimestamp(int(stop['scheduledDepartureTime']))
			arrival_time  = datetime.utcfromtimestamp(int(stop['scheduledArrivalTime']))
			dotw = date.weekday()
			weekend = dotw > 4
			month = date.month
			seconds_since_midnight = get_seconds_since_midnight(date)
			expected_time_station = (departure_time - arrival_time).total_seconds()

			station_info = stations_df[stations_df['URI'] == station_cur_uri].iloc[0, :]
			station_lng = station_info['longitude']
			station_lat = station_info['latitude']
			station_stop = station_info['avg_stop_times']

			vector = [station_cur, str(dotw), weekend, month, seconds_since_midnight, expected_time_station, station_lng, station_lat, station_stop, train_type, line_id, stop_arr, stop_dep, line]

			before = time.time()
			delay = cat.predict([vector])[0]
			after = time.time()
			print(f'Prediction: {after-before} sec.')

			delays.append((stop['station'], stop['time'], delay))
		except Exception as e:
			raise e
			delays.append((stop['station'], stop['time'], np.NaN))
	return delays


print(get_features('BE.NMBS.IC527', '11-07-2019 15:00'))