#!/usr/bin/env python
from tornado.web import RequestHandler

class RootHandler(RequestHandler):
    def get(self):
        self.write({'message': 'hello world'})

