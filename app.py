#!/usr/bin/env python
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop
from root import RootHandler
from connections import ConnectionsHandler

if __name__ == "__main__":
    urls = [("/", RootHandler),
    ("/connections", ConnectionsHandler)]
    app = Application(urls, debug=True)
    app.listen(3000)
    IOLoop.instance().start()
