'''
Created on 27 Apr 2015

@author: Mark
'''
import logging
import socket
import time
from config import config

MBED_ECHO_PORT = config.get_mbed_echo_port()
OSD_MBEDS = config.get_mbed_osders()
JOB_MBEDS = config.get_mbed_jobbers()
HOSTS = config.get_hosts()
# MBED_ECHO_PORT = config.get_mbed_echo_port("../config/data.json")
# OSD_MBEDS = config.get_mbed_osders("../config/data.json")
# JOB_MBEDS = config.get_mbed_jobbers("../config/data.json")
# HOSTS = config.get_hosts("../config/data.json")


def send(mbed_ip, payload):
    try:
        logging.info("Attempting to connect to MBED %s" % mbed_ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((mbed_ip, MBED_ECHO_PORT))
        s.setblocking(False)
        s.sendall(payload)
        while True:
            data = s.recv(1024)
            if not data:
                break
        s.close()
    except Exception as e:
        logging.info("Failed to connect to MBED %s" % mbed_ip)
        logging.info("Exception - %s" % e)


class OSDConnect():

    def __init__(self, mbed_ip, resx, resy, style, host):
        self.mbed_ip = mbed_ip
        self.resx = resx
        self.resy = resy
        self.style = style
        self.host = host

    def run(self):
        logging.info("MBED %s instructed to connect to HOST %s" %
                     (self.mbed_ip, self.host))
        payload = "{} {} {} {}\0".format(self.resx,
                                         self.resy,
                                         self.style,
                                         self.host)
        send(self.mbed_ip, str.encode(payload))


class SendKeys():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self):
        logging.info("MBED %s instructed to send test string" %
                     self.mbed_ip)
        time.sleep(1)
        send(self.mbed_ip, str.encode("keyboard\0"))


class Exit():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self):
        logging.info("MBED %s instructed to close and exit" %
                     self.mbed_ip)
        time.sleep(1)
        send(self.mbed_ip, str.encode("close\0"))


class MouseMove():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self):
        logging.info("MBED %s instructed to move mouse" % self.mbed_ip)
        send(self.mbed_ip, str.encode("mouse\0"))


if __name__ == "__main__":
        payload = "1920 1080 e 1\0"
        print(payload)
        send("10.10.10.50", str.encode(payload))
