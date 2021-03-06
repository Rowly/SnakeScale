'''
Created on Jun 17, 2016

@author: Mark
'''
import sys
import os
import subprocess
import argparse
import http.server
from urllib.parse import urlparse, parse_qs
try:
    from config import config
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from config import config

CON = None
PORT = config.get_host_port()
HEADER_TEXT = ("<html>" +
               "<head profile='http://www.w3.org/2005/10/profile'>" +
               "<title>Control Server </title>" +
               "<link rel='icon' type='image.png' href='http://example.com/myicon.png'>" +
               "</head>")


class ControlServer(http.server.BaseHTTPRequestHandler):

    """
    Inbound request methods:
    /api?command=<command>&device=<device>
    /api?command=start&device=<device>&test_type=<type>&resolution=<1902x1080>
    /api?comand=stop
    """
    def do_GET(self):
        global CON
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(HEADER_TEXT, "UTF-8"))
            self.wfile.write(bytes("<body>" +
                                   "<p>This is the ControlServer.</p>" +
                                   "<p>Usage:</p>" +
                                   "<p>/api?command=start&device=ddx30&test_type=exclusive&resolution=1920x1080</p>" +
                                   "<p>/api?command=stop" +
                                   "</body></html>", "UTF-8"))
        else:
            o = urlparse(self.path)
            query = parse_qs(o.query)
            if "command" in query:
                command = query["command"][0]
                if command == "start":
                    if "device" in query:
                        device = query["device"][0].lower()
                    else:
                        self.send_response(400)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        return
                    if "test_type" in query:
                        test_type = query["test_type"][0]
                    else:
                        self.send_response(400)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        return
                    if "resolution" in query:
                        resolution = query["resolution"][0]
                    else:
                        self.send_response(400)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        return
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(HEADER_TEXT, "UTF-8"))
                    self.wfile.write(bytes("<body>" +
                                           "<p>STARTED</p>" +
                                           "</body></html>", "UTF-8"))
                    CON = subprocess.Popen(["python3",
                                            "controller.py",
                                            device,
                                            test_type,
                                            resolution])
                elif command == "stop":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(HEADER_TEXT, "UTF-8"))
                    self.wfile.write(bytes("<body>" +
                                           "<p>STOPPED</p>" +
                                           "</body></html>", "UTF-8"))
                    try:
                        if CON is not None:
                            CON.kill()
                    except Exception as e:
                        print("Tried to kill controller.py but can't {}"
                              .format(e))
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Control Server")
        parser.add_argument("ip", type=str, help="IP of Server")
        args = parser.parse_args()
        ip = args.ip
        server = http.server.HTTPServer((ip, PORT), ControlServer)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
