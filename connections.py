#!/usr/bin/env python
from tornado.web import RequestHandler, HTTPError, MissingArgumentError
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode
from datetime import datetime
from classifier import Classifier

import time as tm
import json
import re
import os.path
from random import randint

CONNECTIONS_API_URL = 'http://api.irail.be/connections/?from={}&to={}&time={}&date={}&timesel={}&format=json'
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_REQUEST = 400
SECONDS_TO_MINUTES_DIV = 60
MIN_15 = 60 * 15
# demo: http://localhost:3000/connections?from=Vilvoorde&to=Brugge&time=1138&date=080719&timesel=departure

class ConnectionsHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')

    def get_buckets(self, vehicle_id, data_type, station):
        bucket_list = {}
        if os.path.isfile('data/splitted/results/2018/{}.json'.format(vehicle_id)):
            with open('data/splitted/results/2018/{}.json'.format(vehicle_id)) as f:
                departure_data = json.load(f)
                station_data = departure_data[station][data_type]['raw']
                for i in range(0, 17):
                    bucket_list[i] = 0

                station_data = sorted(station_data)
                for entry in station_data:
                    if entry < 0:
                        bucket_list[0] += 1
                    elif entry > MIN_15:
                        bucket_list[16] += 1
                    else:
                        bucket_list[entry//SECONDS_TO_MINUTES_DIV] += 1
        return bucket_list

    async def get(self):
        try:
            departure_station = self.get_query_argument('from')
            arrival_station = self.get_query_argument('to')
            time = self.get_query_argument('time')
            date = self.get_query_argument('date')
            timesel = self.get_query_argument('timesel')
        except MissingArgumentError:
            raise HTTPError(status_code=HTTP_BAD_REQUEST,
                            log_message='Missing required arguments for the iRail /connections API')

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

                connection['departure']['reliability'] = self.get_buckets(departure_vehicle_id, 'departure', departure_station)
                connection['arrival']['reliability'] = self.get_buckets(arrival_vehicle_id, 'arrival', arrival_station)

                if 'vias' in connection and len(connection['vias']['via']) > 1:
                    for via in connection['vias']['via']:
                        via_station = via['stationinfo']['@id']
                        departure_vehicle_id = via['departure']['vehicle'].split('.')[-1]
                        arrival_vehicle_id = via['arrival']['vehicle'].split('.')[-1]
                        via['departure']['reliability_graph'] = self.get_buckets(departure_vehicle_id, 'departure', via_station)
                        via['arrival']['reliability_graph'] = self.get_buckets(arrival_vehicle_id, 'arrival', via_station)


            # Return response
            response['connection'] = response['connection'][0]
            self.write(response)
        else:
            raise HTTPError(status_code=HTTP_INTERNAL_SERVER_ERROR,
                            log_message='Missing required arguments for the iRail /connections API')

    async def _get_routes(self, departure_station, arrival_station, time, date, timesel):
        '''
        Performs a request to the iRail /connections API.
        Input:
            - departure_station
            - arrival_station
            - datetime
            - timesel
        Output:
            - JSON response as a Python dict
        '''
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(CONNECTIONS_API_URL.format(departure_station,
                                                                          arrival_station,
                                                                          time,
                                                                          date,
                                                                          timesel))
            response = json_decode(response.body)
        except Exception as e:
            print('Error: %s' % e)
            return None
        else:
            return response

        # Free resources again
        http_client.close()
