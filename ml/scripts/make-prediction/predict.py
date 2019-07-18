import pandas as pd
import numpy as np
import json
import re
import requests
import time
import pickle
from datetime import datetime
from catboost import CatBoostRegressor, Pool

y_min = -984.0000000000001

before = time.time()
cat = CatBoostRegressor()
cat.load_model('test_model.cbm')
after = time.time()
print(f'Loading model: {after-before} sec.')

stations_df = pd.read_csv('../../data/stations.csv')
station_uris = json.load(open('../../data/station_uris_irail.json', 'r'))
encoders = pickle.load(open('encoders.pickle', 'rb'))


def station_to_uri(station):
	try:
		return station_uris[station]
	except KeyError:
		return None


def get_seconds_since_midnight(datetime):
	midnight = datetime.replace(hour=0, minute=0, second=0, microsecond=0)
	return (datetime - midnight).total_seconds()


def get_line_number(vehicle):
	# Expected input: "IC1515"
	pattern = re.compile("^([A-Z]+)([0-9]+)$")
	vehicle_type = pattern.match(vehicle).group(1)
	vehicle_nr = int(pattern.match(vehicle).group(2))
	line_nr = 0
	if vehicle_type == 'IC':
		line_nr = int(100 * np.floor(vehicle_nr / 100))
	elif vehicle_type == 'L':
		line_nr = int(50 * np.floor(vehicle_nr / 50))
	elif vehicle_type == 'S':
		line_nr = int(50 * np.floor(vehicle_nr / 50))
	else:
		line_nr = 'P'
	return vehicle_nr, line_nr


def encode(feature, value):
	return encoders[feature].transform([value])


def get_features(vehicle_id, time_str):
	parsed_time = pd.to_datetime(time_str, format='%d-%m-%Y %H:%M')
	parsed_time_str = parsed_time.strftime('%d%m%y')
	VEHICLE_URL = 'http://api.irail.be/vehicle/?id={}&date={}&format=json&lang=nl'.format(
	    vehicle_id, parsed_time_str
	)

	line_id = vehicle_id.split('.')[-1]
	pattern = re.compile("^([A-Z]+)([0-9]+)$")
	train_type = pattern.match(line_id).group(1)
	# vehicle_nr, line = get_line_number(line_id)

	resp = requests.get(VEHICLE_URL)
	resp = json.loads(resp.content)
	uri_dep = resp['stops']['stop'][0]['stationinfo']['@id']  # Name of the departure station
	stop_dep = int(stations_df[stations_df['URI'] == uri_dep].iloc[0, :]['avg_stop_times'])
	station_dep = uri_dep.split('/')[-1]
	uri_arr = resp['stops']['stop'][-1]['stationinfo']['@id']
	stop_arr = int(stations_df[stations_df['URI'] == uri_arr].iloc[0, :]['avg_stop_times'])
	station_arr = uri_arr.split('/')[-1]
	line = f'{uri_dep}_{uri_arr}'

	delays = []
	for stop in resp['stops']['stop']:
		try:
			station_cur_uri = station_to_uri(stop['station'])
			station_cur = station_cur_uri.split('/')[-1]
			date = datetime.utcfromtimestamp(int(stop['time']))
			departure_time = datetime.utcfromtimestamp(int(stop['scheduledDepartureTime']))
			arrival_time = datetime.utcfromtimestamp(int(stop['scheduledArrivalTime']))
			dotw = date.weekday()
			weekend = dotw > 4
			month = date.month
			seconds_since_midnight = get_seconds_since_midnight(date)
			expected_time_station = (departure_time - arrival_time).total_seconds()

			station_info = stations_df[stations_df['URI'] == station_cur_uri].iloc[0, :]
			station_lng = station_info['longitude']
			station_lat = station_info['latitude']
			station_stop = station_info['avg_stop_times']

			encoded_data = [dotw, station_cur, line_id, train_type, station_arr, station_dep, line]
			encoded_features = ['dotw', 'station_cur', 'line_id', 'train_type', 'station_arr', 'station_dep', 'line']
			encoded = {}
			for value, feature in zip(encoded_data, encoded_features):
				encoded[feature] = encoders[feature].transform([value])

			vector = [
			    encoded['station_cur'], encoded['station_dep'], encoded['station_arr'],
			    encoded['dotw'], weekend, month, seconds_since_midnight, expected_time_station,
			    station_lng, station_lat, station_stop, encoded['train_type'], encoded['line_id'],
			    stop_arr, stop_dep, encoded['line']
			]

			before = time.time()
			delay = cat.predict([vector])[0]
			delay = np.exp(delay) - 2 + y_min  # NOTE: Model is trained on logarithm!!
			after = time.time()
			# print(f'Prediction: {after-before} sec.')

			delays.append((stop['station'], stop['time'], delay))
		except Exception as e:
			raise e
			delays.append((stop['station'], stop['time'], np.NaN))
	return delays


start = time.time()
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:00'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:01'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:02'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:03'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:04'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:05'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:06'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:07'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:08'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:09'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:10'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:11'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:12'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:13'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:14'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:15'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:16'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:17'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:18'))
print(get_features('BE.NMBS.IC1517', '11-07-2019 15:19'))
end = time.time()
print(end - start)
