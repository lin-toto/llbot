#!/usr/bin/env python2

from proxy2 import *

class SIFRequestHandler(ProxyRequestHandler):

    def response_handler(self, req, req_body, res, res_body):
        print(req.path)