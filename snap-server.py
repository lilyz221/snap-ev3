from __future__ import print_function

import os
import sys
import urlparse

from SimpleHTTPServer import SimpleHTTPRequestHandler
import SocketServer


class Ev3Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/ev3/"):
            url = urlparse.urlparse(self.path)
            endpoint = url.path[len("/ev3/"):]
            params = urlparse.parse_qs(self.path)
            return self.handle_ev3_request(endpoint, params)
        
        if self.path == "/":
            # Serve the main Snap! page instead of the directory listing
            self.path = "/snap.html"

        SimpleHTTPRequestHandler.do_GET(self)

    def handle_ev3_request(self, endpoint, params):
        print("endpoint:", endpoint)
        print("params:", params)

        self.send_response(200)
        self.end_headers()
        self.wfile.write("endpoint = {}\n".format(endpoint))
        

port = 9000
if len(sys.argv) > 1:
    port = int(sys.argv[1])

os.chdir("snap")
    
server = SocketServer.TCPServer(("", port), Ev3Handler)
server.serve_forever()
