#!/usr/bin/env python
import json
import datetime
from gino import Gino
from tornado.web import RequestHandler, MissingArgumentError
CREDENTIALS_FILE = "credentials.json"
POSTGRES_URI = "postgresql://{}:{}@{}:{}/rdb"

db = Gino()

class Infrabel(db.Model):
    __tablename__ = "infrabel"

    id = db.Column(db.Integer(), primary_key=True)
    vehicle_uri = db.Column(db.String(), default="NA")
    vehicle_departure_station = db.Column(db.String(), default="NA")
    vehicle_arrival_station = db.Column(db.String(), default="NA")
    planned_departure = db.Column(db.DateTime())
    planned_arrival = db.Column(db.DateTime())
    delay_departure = db.Column(db.Integer())
    delay_arrival = db.Column(db.Integer())
    stop = db.Column(db.String())

class ConvertHandler(RequestHandler):
    async def connect_db(self):
        try:
            credentials = None
            with open(CREDENTIALS_FILE) as f:
                credentials = json.load(f)

            # Make sure that we have our credentials
            if not credentials:
                raise Exception()
        except:
            raise Exception("No credentials available for the database")

        await db.set_bind(POSTGRES_URI.format(credentials["user"],
                                              credentials["password"],
                                              credentials["ip"],
                                              credentials["port"]))
        # Create tables
        await db.gino.create_all()

    async def group_entries(self, station, vehicle_type, time_from, time_until):
        results = await Infrabel.query\
                .where(Infrabel.stop == station)\
                .where(time_from < Infrabel.planned_departure)\
                .where(Infrabel.planned_departure < time_until)\
                .where(Infrabel.vehicle_uri.contains(vehicle_type))\
                .gino.all()
        print(results)


    async def get(self):
        # Open connection
        await self.connect_db()

        # Create something
        create = await Infrabel.create(vehicle_uri="http://example.com/IC123",
                                       vehicle_departure_station="http://example2.com",
                                       vehicle_arrival_station="http://example1.com",
                                       planned_departure=datetime.datetime.now(),
                                       planned_arrival=datetime.datetime.now(),
                                       delay_departure=1,
                                       delay_arrival=6,
                                       stop="http://example5.com")
        create = await Infrabel.create(vehicle_uri="http://example.com/L123",
                                       vehicle_departure_station="http://example2.com",
                                       vehicle_arrival_station="http://example1.com",
                                       planned_departure=datetime.datetime.now(),
                                       planned_arrival=datetime.datetime.now(),
                                       delay_departure=1,
                                       delay_arrival=6,
                                       stop="http://example5.com")

        station = "http://example5.com"
        vehicle_type = "IC"
        time_from = datetime.datetime.now() - datetime.timedelta(seconds=1)
        time_until = datetime.datetime.now()
        await self.group_entries(station, vehicle_type, time_from, time_until)

        # Properly close connection
        await db.pop_bind().close()

