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


def send(mbed_ip, payload):
    try:
        logging.info("ADDER: Attempting to connect to MBED %s" % mbed_ip)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((mbed_ip, MBED_ECHO_PORT))
        s.sendall(payload)
        while True:
            data = s.recv(1024)
            if not data:
                break
        s.close()
    except Exception as e:
        logging.info("ADDER: Failed to connect to MBED %s" % mbed_ip)
        logging.info("ADDER: Exception - %s" % e)


class OSDConnect():

    def __init__(self, mbed_ip, host):
        self.mbed_ip = mbed_ip
        self.host = host

    def run(self):
        logging.info("ADDER: MBED %s instructed to connect to RPI %s" %
                     (self.mbed_ip, self.host))
        send(self.mbed_ip, str.encode("connect %s\0" % self.host))


class SendKeys():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self):
        logging.info("ADDER: MBED %s instructed to send test string" %
                     self.mbed_ip)
        time.sleep(1)
        send(self.mbed_ip, str.encode("keyboard\0"))


class Exit():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self):
        logging.info("ADDER: MBED %s instructed to close and exit" %
                     self.mbed_ip)
        time.sleep(1)
        send(self.mbed_ip, str.encode("close\0"))
        time.sleep(1)
        send(self.mbed_ip, str.encode("restart\0"))


class MouseMove():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self):
        logging.info("ADDER: MBED %s instructed to move mouse" % self.mbed_ip)
        send(self.mbed_ip, str.encode("mouse\0"))
