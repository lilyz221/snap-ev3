#!/usr/bin/env python
from __future__ import print_function

import os
import sys
from urllib.parse import urlparse

import ev3dev.ev3 as ev3

import cgi
from http.server import SimpleHTTPRequestHandler
import socketserver


BadRequest = 400
ServiceUnavailable = 503


class Ev3Handler(SimpleHTTPRequestHandler):

    devices = {}

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-type'])
        form = cgi.parse_multipart(self.rfile, pdict)
        code = form['code'][0]
        
        self.send_response(200)
        self.end_headers()

        print(code)
        return
    
    def do_GET(self):
        if self.path.startswith("/ev3/"):
            url = urlparse.urlparse(self.path)
            path = url.path.split("/")
            if len(path) != 5:
                # '', 'ev3', class, port, attribute
                return self.send_error(BadRequest, "Bad request path")
            device_class = path[2]
            port = path[3]
            attribute = path[4].lower()
            params = urlparse.parse_qs(url.query)
            return self.handle_ev3_request(device_class, port, attribute, params)
                
        if self.path == "/":
            # Serve the main Snap! page instead of the directory listing
            self.path = "/snap.html"

        SimpleHTTPRequestHandler.do_GET(self)

        
    def handle_ev3_request(self, device_class, port, attribute, params):
        print("class = {}, port = {}, attribute = {}, params = {}"
              .format(device_class, port, attribute, params))
        
        attribute = attribute.lower()
        
        device = self.find_device(port, device_class)
        if not device.connected:
            if attribute == 'connected':
                return self.send_result(False)
            else:
                return self.send_error("Device not connected")
        
        if "value" in params:
            # This is a write property
            if len(params["value"]) != 1:
                return self.send_error(BadRequest, "Single value expected")
            try:
                device._set_attribute(None, attribute, params["value"][0])
                return self.send_result("ok")
            except AttributeError as err:
                return self.send_error(BadRequest,
                                "Cannot set attribute '{}'".format(attribute))
        else:
            # This is a read property
            if params:
                return self.send_error(BadRequest, "Unexpected parameters")
            _, result = device._get_attribute(None, attribute)
            if result is None:
                return self.send_error(BadRequest,
                                       "Cannot read attribute '{}', path = '{}'"
                                       .format(attribute, device._path))
            return self.send_result(result)
        
        return self.error(BadRequest)


    def find_device(self, port, device_class):
        if port in Ev3Handler.devices:
            device = Ev3Handler.devices[port]
        else:
            device = ev3.Device(device_class, address=port)
            Ev3Handler.devices[port] = device
            print("New device object created, path = " + device._path)
        return device

            
    def send_result(self, value):
        self.send_response(200)
        self.send_header("Cache-control", "no cache")
        self.end_headers()
        self.wfile.write(value)
        self.wfile.write("\n")

        
    def error(self, code):
        self.send_response(code)
        self.send_header("Cache-control", "no cache")
        self.end_headers()

        
def start_server(port):
    os.chdir(os.path.join(os.path.dirname(__file__), "snapOrig"))
    server = socketserver.TCPServer(("", port), Ev3Handler)
    print("starting server")
    server.serve_forever()

    
if __name__ == "__main__":        
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    start_server(port)
