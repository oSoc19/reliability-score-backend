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
        return (dep_time + dep_delay) - (arr_time + arr_delay)

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

    async def get(self):
        try:
            departure_station = self.get_query_argument('from')
            arrival_station = self.get_query_argument('to')
            time = self.get_query_argument('time')
            date = self.get_query_argument('date')
            timesel = self.get_query_argument('timesel')
        except MissingArgumentError:
            raise HTTPError(
                status_code=HTTP_BAD_REQUEST,
                log_message='Missing required arguments for the iRail /connections API'
            )

        # Perform iRail API query
        response = await self._get_routes(departure_station, arrival_station, time, date, timesel)
        if 'connection' in response:
            # Add reliability data to response
            # NOTE: delay info is an integer, rest of iRail API uses strings
            for connection in response['connection']:
                arrival_station = connection['arrival']['stationinfo']['@id']
                departure_station = connection['departure']['stationinfo']['@id']
                departure_vehicle_id = connection['departure']['vehicle'].split('.')[-1]
                arrival_vehicle_id = connection['arrival']['vehicle'].split('.')[-1]

                dep_reliability = self.get_buckets(
                    departure_vehicle_id, 'departure', departure_station
                )
                if dep_reliability is not None:
                    connection['departure']['reliability'] = dep_reliability

                arr_reliability = self.get_buckets(
                    arrival_vehicle_id, 'arrival', arrival_station
                )
                if arr_reliability is not None:
                    connection['arrival']['reliability'] = arr_reliability

                if 'vias' in connection and len(connection['vias']['via']) > 1:
                    for via in connection['vias']['via']:
                        via_station = via['stationinfo']['@id']
                        departure_vehicle_id = via['departure']['vehicle'].split('.')[-1]
                        arrival_vehicle_id = via['arrival']['vehicle'].split('.')[-1]
                        dep_reliability = self.get_buckets(
                            departure_vehicle_id, 'departure', via_station
                        )
                        if dep_reliability is not None:
                            via['departure']['reliability_graph'] = dep_reliability

                        arr_reliability = self.get_buckets(
                            arrival_vehicle_id, 'arrival', via_station
                        )
                        if arr_reliability is not None:
                            via['arrival']['reliability_graph'] = arr_reliability

                        if arr_reliability is not None and dep_reliability is not None:
                            transfer_time = self.get_transfer_time(via['arrival'], via['departure'])
                            via['reliability_transfer_time'] = transfer_time

            # Return response
            self.write(response)
        else:
            raise HTTPError(
                status_code=HTTP_INTERNAL_SERVER_ERROR,
                log_message='Missing required arguments for the iRail /connections API'
            )

    async def _get_routes(self, departure_station, arrival_station, time, date, timesel):
        """
        Performs a request to the iRail /connections API.
        Input:
            - departure_station
            - arrival_station
            - datetime
            - timesel
        Output:
            - JSON response as a Python dict
        """
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(
                CONNECTIONS_API_URL.format(departure_station, arrival_station, time, date, timesel)
            )
            response = json_decode(response.body)
        except Exception as e:
            print('Error: %s' % e)
            return None
        else:
            return response

        # Free resources again
        http_client.close()
