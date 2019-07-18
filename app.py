#!/usr/bin/env python
import asyncio
import datetime
import os
from functools import partial
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from root import RootHandler
from connections import ConnectionsHandler
DEFAULT_PORT = 3000

async def main():
    print('Running main before starting server...')
    print(await c.predict('IC527', datetime.datetime.now()))

if __name__ == '__main__':
    urls = [('/', RootHandler),
    ('/connections', ConnectionsHandler)]

    # Only enable debug mode when the 'DEBUG' environment variable exists
    debug_mode = False
    if 'DEBUG' in os.environ:
        debug_mode = True
    app = Application(urls, debug=debug_mode)

    # Perform prediction calculations before starting the server
    #IOLoop.instance().run_sync(main)

    # Start the server
    app.listen(os.getenv('PORT', DEFAULT_PORT))
    IOLoop.instance().start()
