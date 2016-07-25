"""
Created on 27 Apr 2015

@author: Mark

This class runs on each HOST machine in
the setup. It is a basic HTTPServer that listens for
GET requests sent by the test controller running controller.py
through the use of the pi_jobs modules.

"""
import sys
import os
import platform
import subprocess
import logging
import http.server
from urllib.parse import urlparse, parse_qs
import time
import json
import argparse
import random
from collections import OrderedDict
from multiprocessing import Process
try:
    from jobs.mbed_jobs import OSDConnect, SendKeys, MouseMove,\
        CloseGui, Disconnect, Av4proConnect
    from config import config
    from utilities import test_usb
    from utilities.test_video import Video
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from jobs.mbed_jobs import OSDConnect, SendKeys, MouseMove,\
        CloseGui, Disconnect, Av4proConnect
    from config import config
    from utilities import test_usb
    from utilities.test_video import Video


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
RESULT = OrderedDict()


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
        global RESULT
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
#
#                     system = platform.system()
#                     if system == "Win32" or system == "Windows":
#                         suffix = ""
#                         path = ""
#                     else:
#                         suffix = "3"
#                         path = "./"
#                     try:
#                         gui = subprocess.Popen(["python{}".format(suffix),
#                                                 "{}utilities/capture_gui.py"
#                                                 .format(path)])
#                         if device == "ddx30" and test_type == "view":
#                             time.sleep(45)
#                             gui.kill()
#                     except SystemExit:
#                         pass
#
#                     f = os.path.abspath("{}dump/test.txt".format(path))
#                     with open(f, "w"):
#                         pass

                    if device == "ddx30":
                        if DEBUG:
                            key = "1"
                            print(DEBUG)
                            print(key)
                        else:
                            key = str(random.randint(1, len(OSD_MBEDS)))
                        if host == "Ubuntu":
                            target = random.choice(["1", "2", "3",
                                                    "4", "5", "6",
                                                    "7", "8", "9",
                                                    "10"])
                        elif host == "Win7":
                            target = random.choice(["11", "12", "13",
                                                    "14", "15", "16",
                                                    "17", "18", "19",
                                                    "20"])
                        if DEBUG:
                            print(target)

                        if test_type == "view":
                            self.ddx_view(host, key, resolution_x,
                                          resolution_y, target)
                        elif test_type == "shared":
                            self.ddx_shared(host, key, resolution_x,
                                            resolution_y, target)
                        elif test_type == "exclusive":
                            pass
                        elif test_type == "private":
                            pass
                        elif test_type == "all":
                            self.ddx_view(host, key, resolution_x,
                                          resolution_y, target)
                            self.ddx_shared(host, key, resolution_x,
                                            resolution_y, target)

                    elif device == "av4pro":
                        channel = test_type
                        self.start_gui(device)
                        Av4proConnect(channel).run()
                        time.sleep(15)
                        SendKeys(JOB_MBEDS[key]).run()
                        MouseMove(JOB_MBEDS[key]).run()
                        CloseGui(JOB_MBEDS[key]).run()
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
                    if device == "ddx30":
                        data = json.dumps(RESULT, indent=4)
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(bytes(data, "UTF-8"))

    def ddx_view(self, host, key, resolution_x, resolution_y, target):
        global RESULT
        RESULT.clear()
        device = "ddx30"
        test_type = "shared"
        style = "v"
        single = OrderedDict()
        multi = OrderedDict()
        channel = OrderedDict()
        """
        View Connection:
        - Single connection
        - Multiple connections
        """
        self.start_gui(device, test_type)
        OSDConnect(OSD_MBEDS[key],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(15)
        MouseMove(JOB_MBEDS[key]).run()
        SendKeys(JOB_MBEDS[key]).run()
        CloseGui(JOB_MBEDS[key]).run()
        single_video = Video()
        single_video.set(host, key)
        channel.update({"Console": key,
                        "Computer": target
                        }
                       )
        single.update({"Channel": channel,
                       "mouse": test_usb.mouse(),
                       "keyboard": test_usb.key_b(),
                       "video": single_video.get()
                       }
                      )
        RESULT.update({"Single": single
                       }
                      )
        Disconnect(JOB_MBEDS[key]).run()
        time.sleep(3)

        key_2 = self.get_second_key(key)
        channel.clear()
        OSDConnect(OSD_MBEDS[key],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(1)
        OSDConnect(OSD_MBEDS[key_2],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(15)
        mutli_video = Video()
        mutli_video.set(host, key)
        mutli_video.set(host, key_2)
        channel.update({"Console 1": key,
                        "Console 2": key_2,
                        "Computer": target
                        }
                       )
        multi.update({"Channel": channel,
                      "video": mutli_video.get()
                      }
                     )
        RESULT.update({"Multi": multi
                       }
                      )
        Disconnect(JOB_MBEDS[key]).run()
        Disconnect(JOB_MBEDS[key_2]).run()
        time.sleep(3)

    def ddx_shared(self, host, key, resolution_x, resolution_y, target):
        global RESULT
        RESULT.clear()
        single = OrderedDict()
        multi_nc = OrderedDict()
        multi_c = OrderedDict()
        channel = OrderedDict()
        device = "ddx30"
        test_type = "shared"
        style = "s"
        """
        Shared Connection:
        - Single connection
        - Multiple connections
        -- No contention
        -- With contention
        """
        # single
        self.start_gui(device, test_type)
        OSDConnect(OSD_MBEDS[key],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(15)
        MouseMove(JOB_MBEDS[key]).run()
        SendKeys(JOB_MBEDS[key]).run()
        CloseGui(JOB_MBEDS[key]).run()
        single_video = Video()
        single_video.set(host, key)
        channel.update({"Console": key,
                        "Computer": target})
        single.update({"Channel": channel,
                       "mouse": test_usb.mouse(),
                       "keyboard": test_usb.key_b(),
                       "video": single_video.get()
                       }
                      )
        RESULT.update({"Single": single
                       }
                      )
        Disconnect(JOB_MBEDS[key]).run()
        time.sleep(3)

        # multi
        # no contention
        self.start_gui(device, test_type)
        key_2 = self.get_second_key(key)
        channel.clear()
        OSDConnect(OSD_MBEDS[key],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(1)
        OSDConnect(OSD_MBEDS[key_2],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(15)
        SendKeys(JOB_MBEDS[key]).run()
        SendKeys(JOB_MBEDS[key_2]).run()
        CloseGui(JOB_MBEDS[key_2]).run()

        mutli_video = Video()
        mutli_video.set(host, key)
        mutli_video.set(host, key_2)
        channel.update({"Console 1": key,
                        "Console 2": key_2,
                        "Computer": target})
        multi_nc.update({"Channel": channel,
                         "keyboard": test_usb.key_b(style="non-contention"),
                         "video": mutli_video.get()
                         }
                        )
        RESULT.update({"Non Contention": multi_nc
                       }
                      )
        Disconnect(JOB_MBEDS[key]).run()
        Disconnect(JOB_MBEDS[key_2]).run()
        time.sleep(3)

        # contention
        self.start_gui(device, test_type)
        channel.clear()
        OSDConnect(OSD_MBEDS[key],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(1)
        OSDConnect(OSD_MBEDS[key_2],
                   resolution_x,
                   resolution_y,
                   style,
                   target).run()
        time.sleep(15)

        p1 = Process(target=SendKeys(JOB_MBEDS[key]).run)
        p2 = Process(target=SendKeys(JOB_MBEDS[key_2]).run)
        p1.start()
        time.sleep(0.5)
        p2.start()
        p1.join()
        p2.join()

        time.sleep(0.5)
        CloseGui(JOB_MBEDS[key]).run()

        mutli_video = Video()
        mutli_video.set(host, key)
        mutli_video.set(host, key_2)
        channel.update({"Console 1": key,
                        "Console 2": key_2,
                        "Computer": target}
                       )
        multi_c.update({"Channel": channel,
                        "keyboard": test_usb.key_b(style="contention"),
                        "video": mutli_video.get()
                        }
                       )
        RESULT.update({"Contention": multi_c
                       }
                      )
        Disconnect(JOB_MBEDS[key]).run()
        Disconnect(JOB_MBEDS[key_2]).run()
        time.sleep(3)

    def start_gui(self, device, test_type="none"):
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
                time.sleep(45)
                gui.kill()
        except SystemExit:
            pass

        f = os.path.abspath("{}dump/test.txt".format(path))
        with open(f, "w"):
            pass

    def get_second_key(self, key):
        key_2 = key
        while key_2 == key:
            key_2 = str(random.randint(1, len(OSD_MBEDS)))
        return key_2


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
