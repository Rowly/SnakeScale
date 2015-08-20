'''
Created on 27 Apr 2015

@author: Mark
'''
import requests
import logging
from config import config

RPI_PORT = config.get_rpis_port()
RPIS = config.get_rpis()


class GetResult():

    def __init__(self, rpi, device):
        self.rpi = rpi
        self.device = device

    def run(self):
        logging.info("ADDER: Getting result from RPI %s @ %s" %
                     (self.rpi, RPIS[self.rpi]))
        try:
            r = requests.get("http://" + RPIS[self.rpi] + ":" + RPI_PORT +
                             "/get_result/" + self.device)
            assert(r.status_code == 200)
            logging.info("ADDER: RPI %s gives: %s" %
                         (self.rpi, str(r.json())))
        except Exception:
            logging.info("ADDER: Failed to connect to RPI %s" % self.rpi)


class Notify():

    def __init__(self, rpi, device):
        self.rpi = rpi
        self.device = device

    def run(self):
        logging.info("ADDER: Prepped RPI %s @ %s to run test" %
                     (self.rpi, RPIS[self.rpi]))
        try:
            r = requests.get("http://" + RPIS[self.rpi] + ":" + RPI_PORT +
                             "/notify/" + self.device + "/" + self.rpi)
            assert(r.status_code == 200)
        except Exception:
            logging.info("ADDER: Failed to connect to RPI %s" % self.rpi)
