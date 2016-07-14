"""
Created on 27 Apr 2015

@author: Mark

This class runs on each Raspberry Pi source machine in
the setup. It is a basic HTTPServer that listens for
GET requests sent by the test controller running controller.py
through the use of the pi_jobs modules.

"""
import sys
import os
import subprocess
import logging
import http.server
from urllib.parse import urlparse, parse_qs
import time
import json
import argparse
import random
import platform
try:
    from jobs import mbed_jobs
    from config import config
    from utilities import test_video, test_usb, capture_gui
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from jobs import mbed_jobs
    from config import config
    from utilities import test_video, test_usb, capture_gui


HOST_PORT = config.get_host_port()
HOSTS = config.get_hosts()
OSD_MBEDS = config.get_mbed_osders()
JOB_MBEDS = config.get_mbed_jobbers()
ALIFS = config.get_alifs()
DEBUG = False
BUSY = False
HEADER_TEXT = ("<html>" +
               "<head profile='http://www.w3.org/2005/10/profile'>" +
               "<title>Host Server</title>" +
               "<link rel='icon' type='image.png' href='http://example.com/myicon.png'>" +
               "</head>")
BODY_TEXT = ("<body>" +
             "<p>This is the ControlServer.</p>" +
             "<p>Usage:</p>" +
             "<p>/api?command=notify&device=ddx30&hosts=1&test_type=exclusive&resolution=1920x1080</p>" +
             "<p>/api?command=get_result&device=ddx30&test_type=exclusive" +
             "</body></html>")


def logging_start():
    logging.basicConfig(filename="/var/log/snakescale-ddx/result.log",
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.INFO)
    logging.info("==== Started Logging ====")


def logging_stop():
    logging.info("==== Stopped Logging ====")
    time.sleep(1)
    logging.shutdown()


class RemoteServer(http.server.BaseHTTPRequestHandler):

    """
    Inbound request methods:
    /<command>/<device>/<host>
    /notify/<device>/<host>
    /get_result/<device>
    """
    def do_GET(self):
        global BUSY
        global DEBUG

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(HEADER_TEXT, "UTF-8"))
            self.wfile.write(bytes(BODY_TEXT, "UTF-8"))
        else:
            o = urlparse(self.path)
            query = parse_qs(o.query)
            if "command" in query:
                command = query["command"][0]
                """
                NOTIFY
                """
                if command == "notify":
                    if "device" in query:
                        device = query["device"][0].lower()
                    else:
                        self.send_response(400)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        return
                    if "host" in query:
                        host = query["host"][0]
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
                        resolution = resolution.split("x")
                        resolution_x = resolution[0]
                        resolution_y = resolution[1]
                    else:
                        self.send_response(400)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        return
                    logging.info("Received notice to run test for %s"
                                 % device)
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()

                    BUSY = True

                    system = platform.system()
                    if system == "Win32" or system == "Windows":
                        suffix = ""
                        path = ""
                    else:
                        suffix = "3"
                        path = "./"
                    try:
                        gui = subprocess.Popen(["python{}".format(suffix),
                                                "{}utilities/capture_gui.py"
                                                .format(path)])
                        if device == "ddx30" and test_type == "view":
                            time.sleep(5)
                            gui.kill()
                    except SystemExit:
                        pass

                    f = os.path.abspath("{}dump/test.txt".format(path))
                    with open(f, "w"):
                        pass

                    if device == "ddx30":
                        if DEBUG:
                            key = "1"
                        else:
                            key = str(random.randint(1, len(OSD_MBEDS)))
                        print(DEBUG)
                        print(key)
                        if test_type == "view":
                            style = "v"
                        elif test_type == "shared":
                            style = "s"
                        elif test_type == "exclusive":
                            style = "e"
                        elif test_type == "private":
                            style = "p"
                        if host == "Ubuntu":
                            target = random.choice(["1", "2", "3",
                                                    "4", "5", "6",
                                                    "7", "8", "9",
                                                    "10"])
                            print(target)
                        elif host == "Win7":
                            target = random.choice(["11", "12", "13",
                                                    "14", "15", "16",
                                                    "17", "18", "19",
                                                    "20"])
                            print(target)
                        mbed_jobs.OSDConnect(OSD_MBEDS[key],
                                             resolution_x,
                                             resolution_y,
                                             style,
                                             target).run()
                        time.sleep(15)
                        mbed_jobs.SendKeys(JOB_MBEDS[key]).run()
                        mbed_jobs.MouseMove(JOB_MBEDS[key]).run()
                        mbed_jobs.Exit(JOB_MBEDS[key]).run()
#                             test_video.Capture(ALIFS[key]).run()
                        mbed_jobs.Disconnect(JOB_MBEDS[key]).run()
                        time.sleep(3)
                    elif device == "av4pro":
                        mbed_jobs.Av4proConnect(test_type).run()
                        time.sleep(15)
                        mbed_jobs.SendKeys(JOB_MBEDS[key]).run()
                        mbed_jobs.MouseMove(JOB_MBEDS[key]).run()
                        mbed_jobs.Exit(JOB_MBEDS[key]).run()
                        time.sleep(3)

                    BUSY = False
                elif command == "get_result":
                    """
                    GET RESULT
                    """
                    if "device" in query:
                        device = query["device"][0].lower()
                    else:
                        self.send_response(400)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        return
                    if BUSY is True:
                        self.send_response(200)
                        self.send_header("Content-type", "test/plain")
                        self.end_headers()
                        self.wfile.write(bytes("busy", "UTF-8"))
                    logging.info("Controller attempting to get results")
                    if device == "ddx30" or device == "av4pro":
                        mouse = test_usb.mouse()
                        keyb = test_usb.key_b()
                        """
                        TODO: When adding video back in, Windows path
                        will need to be used
                        """
    #                   video = test_video.ImageCompare().run()
                        data = json.dumps({"mouse": mouse,
                                           "keyb": keyb}, indent=4)
    #                   data = json.dumps({"mouse": mouse,
    #                                      "keyb": keyb,
    #                                      "video": video}, indent=4)
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(bytes(data, "UTF-8"))


try:
    parser = argparse.ArgumentParser(description="Remote Server")
    parser.add_argument("ip", type=str, help="IP of Server")
    parser.add_argument("--debug", dest="debug", action="store_true",
                        help="Force to use console 1 only")
    parser.set_defaults(debug=False)

    args = parser.parse_args()
    ip = args.ip
    DEBUG = args.debug
    logging_start()
    server = http.server.HTTPServer((ip, HOST_PORT), RemoteServer)
    logging.info("Started Server on %s" % ip)
    server.serve_forever()
except KeyboardInterrupt:
    server.socket.close()
    logging.info("Stopping Server on %s" % ip)
    logging_stop()
    server.socket.close()
