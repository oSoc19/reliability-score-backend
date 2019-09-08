#!/usr/bin/env python
from tornado.web import RequestHandler, HTTPError, MissingArgumentError
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode
from datetime import datetime

import time as tm
import json
import re
import os.path
from random import randint

CONNECTIONS_API_URL = 'http://api.irail.be/connections/?from={}&to={}&time={}&date={}&timesel={}&format=json'
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_REQUEST = 400
HTTP_OK = 200
SECONDS_TO_MINUTES_DIV = 60
MAX_BUCKET = 15
NEGATIVE_DELAY = 0
SPLIT_PATH = 'data/splitted/2019/{}.json'
PRECISION = 1
# demo: http://localhost:3000/connections?from=Vilvoorde&to=Brugge&time=1138&date=080719&timesel=departure


class ConnectionsHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')

    def get_transfer_time(self, arrival, departure):
        arr_time = int(arrival['time'])
        arr_graph = arrival['reliability_graph']
        dep_time = int(departure['time'])
        dep_graph = departure['reliability_graph']

        arr_delay = max(arr_graph, key=lambda k: arr_graph[k])
        dep_delay = max(dep_graph, key=lambda k: dep_graph[k])
        return ((dep_time + dep_delay) - (arr_time + arr_delay)) * 60

    def get_buckets(self, vehicle_id, data_type, station):
        bucket_list = {}
        if os.path.isfile(SPLIT_PATH.format(vehicle_id)):
            with open(SPLIT_PATH.format(vehicle_id)) as f:
                data = json.load(f)

                # In case the station isn't available for the vehicle, return None
                if not station in data:
                    return None

                station_data = data[station][data_type]['raw']
                for i in range(0, MAX_BUCKET + 2):  # One extra for negative delays (index 0) and for above 15 (index 16)
                    bucket_list[i] = 0

                station_data = sorted(station_data)
                for entry in station_data:
                    if entry < 0:
                        bucket_list[NEGATIVE_DELAY] += 1
                    elif entry > MAX_BUCKET * 60:
                        bucket_list[MAX_BUCKET + 1] += 1
                    else:
                        bucket_list[entry // SECONDS_TO_MINUTES_DIV + 1] += 1

            # Convert to percentages
            number_of_entries = sum(bucket_list.values())
            for b in bucket_list:
                bucket_list[b] = round(100 * (bucket_list[b] / number_of_entries), PRECISION)


            return bucket_list
        else:
            return None

    def handle_invalid_vehicle_id(self, vehicle_id):
        # S trains are mapped on L trains in the data
        # Train number are always the last 4 digits, but we have S51 and S1
        # trains for example
        if 'S' in vehicle_id:
            vehicle_id = 'L' + vehicle_id[-4:]

        # ICT and ICL trains are the same as IC trains
        if 'IC' in vehicle_id:
            if os.path.isfile(SPLIT_PATH.format(vehicle_id.replace('IC', 'ICT'))):
                vehicle_id = vehicle_id.replace('IC', 'ICT')

            if os.path.isfile(SPLIT_PATH.format(vehicle_id.replace('IC', 'ICL'))):
                vehicle_id = vehicle_id.replace('IC', 'ICL')

        return vehicle_id

    async def get(self):
        try:
            dep_station = self.get_query_argument('from')
            arr_station = self.get_query_argument('to')
            time = self.get_query_argument('time')
            date = self.get_query_argument('date')
            timesel = self.get_query_argument('timesel')
        except MissingArgumentError:
            raise HTTPError(
                status_code=HTTP_BAD_REQUEST,
                log_message='Missing required arguments for the iRail /connections API'
            )

        # Perform iRail API query
        response, status_code = await self._get_routes(dep_station, arr_station, time, date, timesel)
        print(response)
        print(status_code)

        if status_code == HTTP_OK and 'connection' in response:
            # Add reliability data to response
            # NOTE: delay info is an integer, rest of iRail API uses strings
            for connection in response['connection']:
                arr_station = connection['arrival']['stationinfo']['@id']
                dep_station = connection['departure']['stationinfo']['@id']
                dep_vehicle_id = self.handle_invalid_vehicle_id(connection['departure']['vehicle'].split('.')[-1])
                arr_vehicle_id = self.handle_invalid_vehicle_id(connection['arrival']['vehicle'].split('.')[-1])


                dep_reliability = self.get_buckets(dep_vehicle_id,
                                                   'departure',
                                                   dep_station)

                if dep_reliability is not None:
                    connection['departure']['reliability_graph'] = dep_reliability

                if arr_vehicle_id[0] == 'S' and arr_vehicle_id[1].isdigit():
                    arr_vehicle_id = 'L' + arr_vehicle_id[2:]

                arr_reliability = self.get_buckets(arr_vehicle_id,
                                                   'arrival',
                                                   arr_station)
                if arr_reliability is not None:
                    connection['arrival']['reliability_graph'] = arr_reliability

                if 'vias' in connection:
                    for via in connection['vias']['via']:
                        via_station = via['stationinfo']['@id']
                        dep_vehicle_id = self.handle_invalid_vehicle_id(via['departure']['vehicle'].split('.')[-1])
                        arr_vehicle_id = self.handle_invalid_vehicle_id(via['arrival']['vehicle'].split('.')[-1])
                        dep_reliability = self.get_buckets(dep_vehicle_id,
                                                           'departure',
                                                           via_station)
                        if dep_reliability is not None:
                            via['departure']['reliability_graph'] = dep_reliability

                        arr_reliability = self.get_buckets(arr_vehicle_id,
                                                           'arrival',
                                                           via_station)
                        if arr_reliability is not None:
                            via['arrival']['reliability_graph'] = arr_reliability

                        if arr_reliability is not None and dep_reliability is not None:
                            transfer_time = self.get_transfer_time(via['arrival'], via['departure'])
                            via['reliability_transfer_time'] = transfer_time

            # Return response
            self.write(response)
        else:
            raise HTTPError(
                status_code=status_code,
                reason=str(response),
                log_message='Missing required arguments for the iRail /connections API'
            )

    async def _get_routes(self, dep_station, arr_station, time, date, timesel):
        """
        Performs a request to the iRail /connections API.
        Input:
            - dep_station
            - arr_station
            - datetime
            - timesel
        Output:
            - JSON response as a Python dict
        """
        http_client = AsyncHTTPClient()
        status_code = HTTP_INTERNAL_SERVER_ERROR
        try:
            response = await http_client.fetch(
                CONNECTIONS_API_URL.format(dep_station, arr_station, time, date, timesel)
            )
            status_code = response.code
            response = json_decode(response.body)
        except Exception as e:
            print('Error: %s' % e)
            status_code = e.code
            response = json_decode(e.response.body)

        # Free resources again
        http_client.close()

        # Return response
        return response, status_code

