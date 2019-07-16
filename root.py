#!/usr/bin/env python
from tornado.web import RequestHandler

class RootHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')

    def get(self):
        self.write({'message': 'hello world'})

