'''
Created on 27 Apr 2015

@author: Mark
'''
import sys
import os
import logging
import socket
import time
from multiprocessing import Process
try:
    from config import config  # @UnusedImport
except:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from config import config  # @Reimport

DEBUG = False


def send(mbed_ip, payload, path="."):
    global DEBUG
    try:
        MBED_ECHO_PORT = config.get_mbed_echo_port(path)
    except Exception:
        MBED_ECHO_PORT = 7
    end = b":"
    try:
        if DEBUG:
            print(payload)
        logging.info("Attempting to connect to MBED {}".format(mbed_ip))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((mbed_ip, MBED_ECHO_PORT))
        s.sendall(payload)
        total_data = []
        data = ""
        while True:
            data = s.recv(1024)
            if end in data:
                total_data.append(data[:data.find(end)])
                break
            total_data.append(data)
            if len(total_data) > 1:
                last_pair = total_data[-2] + total_data[-1]
                if end in last_pair:
                    total_data[-2] = last_pair[:last_pair.find(end)]
                    total_data.pop()
                    break
        s.close()
    except Exception as e:
        logging.info("Failed to connect to MBED {}".format(mbed_ip))
        logging.info("Exception - {}".format(e))


class OSDConnect():

    def __init__(self, mbed_ip, resx, resy, style, host):
        self.mbed_ip = mbed_ip
        self.resx = resx
        self.resy = resy
        self.style = style
        self.host = host

    def run(self, path="."):
        logging.info("MBED {} instructed to connect to HOST {}"
                     .format(self.mbed_ip, self.host))
        payload = "{} {} {} {}\0".format(self.resx,
                                         self.resy,
                                         self.style,
                                         self.host)
        send(self.mbed_ip, str.encode(payload), path)


class SendKeys():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self, path="."):
        logging.info("MBED {} instructed to send test string"
                     .format(self.mbed_ip))
        time.sleep(1)
        send(self.mbed_ip, str.encode("keyboard\0"), path)


class CloseGui():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self, path="."):
        logging.info("MBED {} instructed to close and exit"
                     .format(self.mbed_ip))
        time.sleep(1)
        send(self.mbed_ip, str.encode("close\0"), path)


class MouseClick():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self, path="."):
        logging.info("MBED {} instructed to click left mouse"
                     .format(self.mbed_ip))
        time.sleep(1)
        send(self.mbed_ip, str.encode("click\0"), path)


class MouseMove():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self, path="."):
        logging.info("MBED {} instructed to move mouse"
                     .format(self.mbed_ip))
        send(self.mbed_ip, str.encode("mouse\0"), path)


class OpenOSD():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self, path="."):
        logging.info("MBED {} instructed to disconnect"
                     .format(self.mbed_ip))
        send(self.mbed_ip, str.encode("disconnect\0"), path)


class Av4proConnect():

    def __init__(self, mbed_ip, channel):
        self.mbed_ip = mbed_ip
        self.channel = channel

    def run(self):
        logging.info("MBED {} instructed to connect AV4pro channel {}"
                     .format(self.mbed_ip, self.channel))
        send(self.mbed_ip, str.encode("channel{}\0".format(self.channel)))


class BBCConnect():

    def __init__(self, mbed_ip, host, channel):
        self.mbed_ip = mbed_ip
        self.host = host
        self.channel = channel

    def run(self):
        host = self.host.replace("bbc", "")
        logging.info("MBED {} instructed to connect AV4pro channel {}"
                     .format(self.mbed_ip, self.channel))
        send(self.mbed_ip, str.encode("bbc {} channel {}\0"
                                      .format(host, self.channel)))


if __name__ == "__main__":
    DEBUG = True
    for host in ["bbc1", "bbc2", "bbc3", "bbc4"]:
        for channel in ["1", "2", "3", "4"]:
            BBCConnect("10.10.10.157", host, channel).run()
#     import subprocess
#     try:
#         gui = subprocess.Popen(["python",
#                                 "../utilities/capture_gui.py"])
#     except SystemExit:
#         pass
#     ips = ["10.10.10.51", "10.10.10.52", "10.10.10.53"]
#     for ip in ips:
#         Process(target=OSDConnect(ip, "1920", "1080", "s", "11").run).start()
#     time.sleep(3)
#     ips = ["10.10.10.151", "10.10.10.152", "10.10.10.153"]
#     for ip in ips:
#         Process(target=MouseMove(ip).run).start()
#         Process(target=SendKeys(ip).run).start()
#     time.sleep(2)
#     CloseGui("10.10.10.151").run()
#     for ip in ips:
#         Process(target=OpenOSD(ip).run).start()
