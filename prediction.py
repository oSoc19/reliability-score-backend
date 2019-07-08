#!/usr/bin/env python
from tornado.web import RequestHandler, MissingArgumentError

import json
import re
from random import randint


def predictDelays(connection):
	connection['delayPrediction'] = randint(-100, 200)
	connection['delayChance'] = randint(0, 100)
	return connection


class PredictionHandler(RequestHandler):
	def get(self):
		connection = self.get_query_argument("connection", default=None)
		if not connection:
			raise MissingArgumentError("Please provide a station or connection URI")

		response = {}

		# Get iRail data, will use actual API in future
		with open('irail-example.json') as file:
			irail = json.load(file)

		# Add reliability score data
		# NOTE: delay info is an integer, rest of iRail API uses strings
		response = irail
		for connection in response['connection']:
			connection['arrival'] = predictDelays(connection['arrival'])
			connection['departure'] = predictDelays(connection['departure'])
			for via in connection['vias']['via']:
				via['arrival'] = predictDelays(via['arrival'])
				via['departure'] = predictDelays(via['arrival'])

		self.write(irail)