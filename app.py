#!/usr/bin/env python
import asyncio
import datetime
import os
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from root import RootHandler
from connections import ConnectionsHandler

async def main():
    p = Predict()
    station = "http://example5.com"
    vehicle_type = "IC"
    time_from = datetime.datetime.now() - datetime.timedelta(seconds=1)
    time_until = datetime.datetime.now()
    await p.group_entries(station, vehicle_type, time_from, time_until)

if __name__ == "__main__":
    urls = [("/", RootHandler),
    ("/connections", ConnectionsHandler)]

    app = Application(urls, debug=True)
    
    # Perform prediction calculations before starting the server
    #IOLoop.instance().run_sync(main)

    # Start the server
    app.listen(os.getenv("PORT", 3000))
    IOLoop.instance().start()
