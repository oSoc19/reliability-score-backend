#!/usr/bin/env python
from tornado.web import RequestHandler, MissingArgumentError

class PredictionHandler(RequestHandler):
    def get(self):
        station = self.get_query_argument("station", default=None)
        connection = self.get_query_argument("connection", default=None)
        if station:
            print("station")
        elif connection:
            print("connection")
        else:
            raise MissingArgumentError("Please provide a station or connection URI")
        self.write({"message": "hello world"})
