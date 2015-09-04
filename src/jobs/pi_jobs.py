'''
Created on 27 Apr 2015

@author: Mark
'''
import requests
import logging
import time
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
        while True:
            try:
                r = requests.get("http://" + RPIS[self.rpi]
                                 + ":" + str(RPI_PORT) +
                                 "/get_result/" + self.device)
                logging.info("ADDER: Assert Get Result response is 200")
                assert(r.status_code == 200)
                if r.content is not "busy":
                    logging.info("ADDER: RPI %s gives: %s" %
                                 (self.rpi, str(r.json())))
                    break
                else:
                    time.sleep(5)
            except Exception as e:
                logging.info("ADDER: Failed to connect to RPI %s" % self.rpi)
                logging.info("ADDER: Exception - %s" % e)
                break


class Notify():

    def __init__(self, rpi, device):
        self.rpi = rpi
        self.device = device

    def run(self):
        logging.info("ADDER: Prepped RPI %s @ %s to run test" %
                     (self.rpi, RPIS[self.rpi]))
        try:
            r = requests.get("http://" + RPIS[self.rpi]
                             + ":" + str(RPI_PORT) +
                             "/notify/" + self.device + "/" + self.rpi)
            logging.info("ADDER: Assert Notify response is 200")
            assert(r.status_code == 200)
        except Exception as e:
            logging.info("ADDER: Failed to connect to RPI %s" % self.rpi)
            logging.info("ADDER: Exception - %s" % e)
