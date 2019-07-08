#!/usr/bin/env python
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode

import json
import re
from random import randint


CONNECTIONS_API_URL = "http://api.irail.be/connections/?from={}&to={}&time={}&date={}&timesel={}&format=json"
HTTP_INTERNAL_SERVER_ERROR = 500
# demo: http://localhost:3000/connections?from=Vilvoorde&to=Brugge&time=1138&date=080719&timesel=departure

class ConnectionsHandler(RequestHandler):
    async def get(self):
        departure_station = self.get_query_argument("from")
        arrival_station = self.get_query_argument("to")
        time = self.get_query_argument("time")
        date = self.get_query_argument("date")
        timesel = self.get_query_argument("timesel")

        # Perform iRail API query
        response = await self._get_routes(departure_station, arrival_station, time, date, timesel)
        if response:
            # Add random reliability data to response
            # NOTE: delay info is an integer, rest of iRail API uses strings
            for connection in response:
                connection['arrival']['delayPrediction'] = randint(-100, 200)
                connection['arrival']['delayChance'] = randint(0, 100)
                connection['departure']['delayPrediction'] = randint(-100, 200)
                connection['departure']['delayChance'] = randint(0, 100)
                for via in connection['vias']['via']:
                    via['arrival']['delayPrediction'] = randint(-100, 200)
                    via['arrival']['delayChance'] = randint(0, 100)
                    via['departure']['delayPrediction'] = randint(-100, 200)
                    via['departure']['delayChance'] = randint(0, 100)
        else:
            self.send_error(HTTP_INTERNAL_SERVER_ERROR)

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
            print("Error: %s" % e)
            return None
        else:
            return response
