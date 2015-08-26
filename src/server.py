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
sys.path.append(os.path.dirname(__file__))

import logging
import http.server
from urllib.parse import urlsplit
import time
import json
import argparse
import random
from jobs import mbed_jobs
from config import config
from utilities import test_video, test_usb, capture_gui

PORT = config.get_rpis_port()
PIS = config.get_rpis()
OSD_MBEDS = config.get_mbed_osders()
JOB_MBEDS = config.get_mbed_jobbers()
ALIFS = config.get_alifs()


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
    /<command>/<device>/<rpi>
    /notify/<device>/<rpi>
    /get_result/<device>
    """
    def do_GET(self):
        # Split the inbound uri on / to determine info
        u = urlsplit(self.path)
        path = u.path.split("/")
        command = path[1]  # First is the command
        device = path[2]  # Second is the device
        rpi = path[3]  # Third is the index of the Pi itself

        if command == "notify":
            logging.info("Received notice to execute test for %s" % device)

            capture_gui.main()

            if device == "DDX30":
                mbeds_key = str(random.randint(0, len(OSD_MBEDS) - 1))
                alif_key = mbeds_key

                mbed_jobs.OSDConnect(OSD_MBEDS[mbeds_key], rpi).run()
                mbed_jobs.MouseMove(JOB_MBEDS[mbeds_key]).run()
                mbed_jobs.SendKeys(JOB_MBEDS[mbeds_key]).run()
                test_video.Capture(ALIFS[alif_key]).run()

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

        if command == "get_result":
            logging.info("Controller attempting to get results")
            if device == "DDX30":
                mouse = test_usb.mouse()
                keyb = test_usb.key_b()
                video = test_video.ImageCompare().run()
                data = json.dumps({"mouse": mouse,
                                   "keyb": keyb,
                                   "video": video}, indent=4)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(data, "UTF-8"))


try:
    parser = argparse.ArgumentParser(description="Remote Server")
    parser.add_argument("ip", type=str, help="IP of Server")
    args = parser.parse_args()
    ip = args.ip
    logging_start()
    server = http.server.HTTPServer((ip, PORT), RemoteServer)
    logging.info("Started Server on %s" % ip)
    server.serve_forever()
except KeyboardInterrupt:
    server.socket.close()
    logging.info("Stopping Server on %s" % ip)
    logging_stop()
    server.socket.close()
