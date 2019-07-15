#!/usr/bin/env python
import pandas as pd
import numpy as np
import json
import re
from datetime import datetime
from catboost import CatBoostRegressor, Pool
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode
from tornado.ioloop import IOLoop
VEHICLE_API_URL = 'http://api.irail.be/vehicle/?id={}&date={}&format=json&lang=nl'

class Classifier:
    def __init__(self):
        self._cat = CatBoostRegressor()
        self._station_uri_mapping = None
        self._stations = pd.read_csv('data/stations.csv')

        with open('data/station_to_uri_irail.json') as f:
            self._station_uri_mapping = json.load(f)
        self._cat.load_model('data/model.cbm')
        print('Model loaded')

    async def predict(self, vehicle_id, timestamp):
        '''
        Predict the delays for a given vehicle and timestamp.
        - vehicle_id: The ID of the vehicle, for example: IC123
        - timestamp: A complete datetime timestamp
        '''
        # Decode vehicle_nr, line, line_id, vehicle_type
        pattern = re.compile('^([A-Z]+)([0-9]+)$')
        vehicle_type = pattern.match(vehicle_id).group(1)
        line_id = pattern.match(vehicle_id).group(2)
        vehicle_nr, line = self._get_line_number(vehicle_id)
        train_type = vehicle_id

        # Get vehicle information
        response = await self._get_vehicle(vehicle_id, timestamp)
        dep_uri = response['stops']['stop'][0]['stationinfo']['@id'] # Name of the departure station
        stop_dep = int(self._stations[self._stations['URI'] == dep_uri].iloc[0, :]['avg_stop_times'])
        arr_uri = response['stops']['stop'][-1]['stationinfo']['@id']
        stop_arr = int(self._stations[self._stations['URI'] == arr_uri].iloc[0, :]['avg_stop_times'])

        # Predict for every stop
        delays = []
        for stop in response['stops']['stop']:
            try:
                station_cur_uri = self._get_station_uri(stop['station'])
                station_cur = station_cur_uri.split('/')[-1]
                date = datetime.utcfromtimestamp(int(stop['time']))
                departure_time  = datetime.utcfromtimestamp(int(stop['scheduledDepartureTime']))
                arrival_time  = datetime.utcfromtimestamp(int(stop['scheduledArrivalTime']))
                dotw = date.weekday()
                weekend = dotw > 4
                month = date.month
                seconds_since_midnight = self._get_seconds_since_midnight(date)
                expected_time_station = (departure_time - arrival_time).total_seconds()

                station_info = self._stations[self._stations['URI'] == station_cur_uri].iloc[0, :]
                station_lng = station_info['longitude']
                station_lat = station_info['latitude']
                station_stop = station_info['avg_stop_times']

                # Run interference async
                vector = [station_cur, str(dotw), weekend, month, seconds_since_midnight, expected_time_station, station_lng, station_lat, station_stop, train_type, line_id, stop_arr, stop_dep, line]
                delay = await IOLoop.current().run_in_executor(None, self._cat.predict, [vector])
                delay = delay[0] # Read after await, we want to get the first item of the result, not of a Future object

                delays.append((stop['station'], stop['time'], delay))
            except Exception as e:
                print('Error: %s' % e)
                delays.append((stop['station'], stop['time'], np.NaN))
        return delays

    def _get_seconds_since_midnight(self, timestamp):
        midnight = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        return (midnight - timestamp).total_seconds()

    def _get_station_uri(self, station):
        return self._station_uri_mapping.get(station, None)

    def _get_line_number(self, vehicle_id):
        # Expected input: 'IC1515'
        pattern = re.compile('^([A-Z]+)([0-9])+$')
        vehicle_type = pattern.match(vehicle_id).group(1)
        vehicle_nr = int(pattern.match(vehicle_id).group(2))

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

    async def _get_vehicle(self, vehicle_id, timestamp):
        '''
        Performs a request to the iRail /vehicle API.
        Input:
            - vehicle_id
            - timestamp
        Output:
            - JSON response as a Python dict
        '''
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(VEHICLE_API_URL.format(vehicle_id, timestamp.strftime('%d%m%y')))
            response = json_decode(response.body)
        except Exception as e:
            print('Error: %s' % e)
            return None
        else:
            return response

        # Free resources again
        httpclient.close()
