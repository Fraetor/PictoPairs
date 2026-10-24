#! /usr/bin/env python3

"""A little HTTP server that looks for HTML files for extensionless paths.

Original code comes from the cpython's Lib/http/server.py
"""

import argparse
import contextlib
import os
import socket
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer


class STUNHTTPRequestHandler(BaseHTTPRequestHandler):
    """Store and respond with SDP data."""
    def do_PUT(self):
        
        pass


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
