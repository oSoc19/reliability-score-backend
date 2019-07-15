#!/usr/bin/env python
from tornado.web import RequestHandler, HTTPError, MissingArgumentError
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import json_decode

import json
import re
from random import randint

CONNECTIONS_API_URL = "http://api.irail.be/connections/?from={}&to={}&time={}&date={}&timesel={}&format=json"
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_REQUEST = 400
# demo: http://localhost:3000/connections?from=Vilvoorde&to=Brugge&time=1138&date=080719&timesel=departure

class ConnectionsHandler(RequestHandler):
    async def get(self):
        try:
            departure_station = self.get_query_argument("from")
            arrival_station = self.get_query_argument("to")
            time = self.get_query_argument("time")
            date = self.get_query_argument("date")
            timesel = self.get_query_argument("timesel")
        except MissingArgumentError:
            raise HTTPError(status_code=HTTP_BAD_REQUEST,
                            log_message="Missing required arguments for the iRail /connections API")

        # Perform iRail API query
        response = await self._get_routes(departure_station, arrival_station, time, date, timesel)
        if "connection" in response:
            # Add reliability data to response
            # NOTE: delay info is an integer, rest of iRail API uses strings
            for connection in response["connection"]:
                arrival_station = connection["arrival"]["stationinfo"]["@id"]
                departure_station = connection["departure"]["stationinfo"]["@id"]
                connection["reliabilityScore"] = await self._get_score(arrival_station)
                connection["arrival"]["reliability"] = await self._get_reliability(arrival_station)
                connection["departure"]["reliability"] = await self._get_reliability(departure_station)

                for via in connection["vias"]["via"]:
                    via_station = via["stationinfo"]["@id"]
                    via["reliability"] = await self._get_reliability(via_station)

            # Return response
            self.write(response)
        else:
            raise HTTPError(status_code=HTTP_INTERNAL_SERVER_ERROR,
                            log_message="Missing required arguments for the iRail /connections API")

    async def _get_reliability(self, station_uri):
        return randint(0, 100)

    async def _get_score(self, station_uri):
        return randint(1, 3)

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
