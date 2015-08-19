'''
Created on 27 Apr 2015

@author: Mark
'''
import logging
import socket
from root.nested.config import config

MBED_ECHO_PORT = config.get_mbed_echo_port()
OSD_MBEDS = config.get_mbed_osders()
JOB_MBEDS = config.get_mbed_jobbers()
RPIS = config.get_rpis()


def send(mbed_ip, payload):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((mbed_ip, MBED_ECHO_PORT))
        s.sendall(payload)
        while True:
            data = s.recv(1024)
            if not data:
                break
        s.close()
    except Exception:
        logging.info("ADDER: Failed to connect to MBED %s" % mbed_ip)


class OSDConnect():

    def __init__(self, mbed, rpi):
        self.mbed = mbed
        self.rpi = rpi

    def run(self):
        logging.info("ADDER: MBED %s instructed to connect to RPI %s" %
                     (self.mbed, self.rpi))
        send(OSD_MBEDS[self.mbed], str.encode("connect %s\0" % self.rpi))


class SendKeys():

    def __init__(self, alif):
        self.mbed = alif

    def run(self):
        logging.info("ADDER: MBED %s instructed to send test string" %
                     self.mbed)
        send(JOB_MBEDS[self.mbed], str.encode("keyboard\0"))


class MouseMove():

    def __init__(self, alif):
        self.mbed = alif

    def run(self):
        logging.info("ADDER: MBED %s instructed to move mouse" % self.mbed)
        send(JOB_MBEDS[self.mbed], str.encode("mouse\0"))
