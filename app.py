#!/usr/bin/env python
import asyncio
import datetime
import os
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from root import RootHandler
from connections import ConnectionsHandler
from classifier import Classifier

async def main():
    print("Running main before starting server...")
    c = Classifier()
    print(await c.predict("IC527", datetime.datetime.now()))

if __name__ == "__main__":
    urls = [("/", RootHandler),
    ("/connections", ConnectionsHandler)]

    app = Application(urls, debug=True)

    # Perform prediction calculations before starting the server
    #IOLoop.instance().run_sync(main)

    # Start the server
    app.listen(os.getenv("PORT", 3000))
    IOLoop.instance().start()
