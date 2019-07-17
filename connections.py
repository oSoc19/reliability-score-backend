#!/usr/bin/env python
from tornado.web import RequestHandler, HTTPError, MissingArgumentError
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode
from datetime import datetime
from classifier import Classifier

import time as tm
import json
import re
from random import randint

CONNECTIONS_API_URL = 'http://api.irail.be/connections/?from={}&to={}&time={}&date={}&timesel={}&format=json&lang=nl'
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_REQUEST = 400
DELAY_6_MIN = 6 * 60
DELAY_10_MIN = 10 * 60
# demo: http://localhost:3000/connections?from=Vilvoorde&to=Brugge&time=1138&date=080719&timesel=departure

# Only init classifier once!
_classifier = Classifier()

class ConnectionsHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')

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
            for index, connection in enumerate(response['connection']):
                arrival_station = connection['arrival']['stationinfo']['@id']
                departure_station = connection['departure']['stationinfo']['@id']
                reliability = await self._get_reliability( connection['departure']['station'],
                                                                connection['departure']['time'],
                                                                connection['departure']['vehicle'])
                connection['arrival']['reliability'] = reliability

                # TODO use better classification, maybe ML?
                connection['reliabilityScore'] = await self._get_score(reliability)

                for via in connection['vias']['via']:
                    via_station = via['stationinfo']['@id']
                    via['reliability'] = await self._get_reliability(
                                                    via['station'],
                                                    via['departure']['time'],
                                                    via['departure']['vehicle'])
                break

            # Return response
            response['connection'] = response['connection'][0]
            self.write(response)
        else:
            raise HTTPError(status_code=HTTP_INTERNAL_SERVER_ERROR,
                            log_message='Missing required arguments for the iRail /connections API')

    async def _get_reliability(self, stop_name, stop_time, vehicle_name):
        vehicle_id = vehicle_name.split('.')[-1]
        timestamp = datetime.utcfromtimestamp(int(stop_time))
        delays = await _classifier.predict(vehicle_id, timestamp)
        for d in delays:
            print(d, stop_name.split('/')[0])
            if stop_name.split('/')[0] in d:
                return d[-1]

        print('Unknown reliability: {}'.format(stop_name))
        return -1

    async def _get_score(self, reliability):
        if reliability > DELAY_6_MIN:
            return 2
        if reliability > DELAY_10_MIN:
            return 1
        else:
            return 3

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
        httpclient.close()

