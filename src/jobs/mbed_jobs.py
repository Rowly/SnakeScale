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
    from config import config
except:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from config import config


def send(mbed_ip, payload, path="."):
    try:
        MBED_ECHO_PORT = config.get_mbed_echo_port(path)
    except Exception:
        MBED_ECHO_PORT = 7
    end = b":"
    try:
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
        print("DEBUG {}".format(payload))
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


class MouseMove():

    def __init__(self, mbed_ip):
        self.mbed_ip = mbed_ip

    def run(self, path="."):
        logging.info("MBED {} instructed to move mouse"
                     .format(self.mbed_ip))
        send(self.mbed_ip, str.encode("mouse\0"), path)


class Disconnect():

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

if __name__ == "__main__":
    import subprocess
    try:
        gui = subprocess.Popen(["python",
                                "../utilities/capture_gui.py"])
    except SystemExit:
        pass
    ips = ["10.10.10.50", "10.10.10.51", "10.10.10.52", "10.10.10.53"]
    for ip in ips:
        Process(target=OSDConnect(ip, "1920", "1080", "s", "1").run).start()
    time.sleep(3)
    ips = ["10.10.10.150", "10.10.10.151",
           "10.10.10.152", "10.10.10.153"]
    for ip in ips:
        Process(target=SendKeys(ip).run).start()
    time.sleep(2)
    CloseGui("10.10.10.150").run()
    for ip in ips:
        Process(target=Disconnect(ip).run).start()
