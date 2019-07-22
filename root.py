#!/usr/bin/env python
from tornado.web import RequestHandler
GITHUB_REPO = 'https://github.com/oSoc19/reliability-score-backend'

class RootHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')

    def get(self):
        self.redirect(GITHUB_REPO, permanent=True)

