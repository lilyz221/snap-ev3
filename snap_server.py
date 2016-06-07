#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import urlparse

import ev3dev.ev3 as ev3

from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer


BadRequest = 400
ServiceUnavailable = 503


class Ev3Handler(SimpleHTTPRequestHandler):

    devices = {}

    def do_GET(self):
        if self.path.startswith("/ev3/"):
            url = urlparse.urlparse(self.path)
            command = url.path.split("/")[2:]
            params = urlparse.parse_qs(url.query)
            return self.handle_ev3_request(command, params)
        
        if self.path == "/":
            # Serve the main Snap! page instead of the directory listing
            self.path = "/snap.html"

        SimpleHTTPRequestHandler.do_GET(self)

        
    def handle_ev3_request(self, command, params):
        print("command:", command)
        print("params:", params)

        class_ = command[0]
        if class_ == 'motor':
            if len(command) < 3:
                return self.send_error(BadRequest,
                                       "Port and property name required")
            port = command[1]
            prop = command[2]
            return self.handle_motor_command(port, prop, params)

        return self.error(BadRequest)


    def find_device(self, port, device_class):

        if port in Ev3Handler.devices:
            device = Ev3Handler.devices[port]
            assert isinstance(device, device_class)
        else:
            device = device_class(port_name=port)
            Ev3Handler.devices[port] = device
        return device

    
    def handle_motor_command(self, port, prop, params):

        motor = self.find_device(port, ev3.Motor)

        if prop == "connected":
            return self.send_result(motor.connected)
        
        if not motor.connected:
            return self.send_error(ServiceUnavailable,
                                   "Motor not connected to this port")
        if prop == '':
            return self.send_error(BadRequest,
                                   "Missing property name")
        
        if "value" in params:
            # This is a write property
            if len(params["value"]) != 1:
                return self.send_error(BadRequest, "Single value expected")
            try:
                setattr(motor, prop, params["value"][0])
                self.send_result("ok")
            except AttributeError as err:
                self.send_error(BadRequest,
                                "Cannot set attribute '{}'".format(prop))
        else:
            # This is a read property
            if params:
                return self.send_error(BadRequest, "Unexpected parameters")
            result = getattr(motor, prop, None)
            if result is None:
                return self.send_error(BadRequest,
                                       "Cannot read attribute '{}'".format(prop))
            self.send_result(result)

            
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
    os.chdir(os.path.join(os.path.dirname(__file__), "snap"))

    server = SocketServer.TCPServer(("", port), Ev3Handler)
    server.serve_forever()

    
if __name__ == "__main__":        
    port = 9000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    start_server(port)
