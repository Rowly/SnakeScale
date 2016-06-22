'''
Created on 27 Apr 2015

@author: Mark
'''
import requests
import logging
import time
from config import config

HOST_PORT = config.get_host_port()
HOSTS = config.get_hosts()


class Notify():

    def __init__(self, device, host, test_type):
        self.device = device
        self.host = host
        self.test_type = test_type

    def run(self):
        logging.info("ADDER: Prepped HOST %s @ %s to run test" %
                     (self.host, HOSTS[self.host]))
        try:
            payload = {"command": "notify",
                       "device": self.device,
                       "hosts": self.host,
                       "test_type": self.test_type}
            r = requests.get("http://" + HOSTS[self.host] +
                             ":" + str(HOST_PORT) +
                             "/api", params=payload)
            logging.info("ADDER: Assert Notify response is 200")
            assert(r.status_code == 200)
        except Exception as e:
            logging.info("ADDER: Failed to connect to HOST %s" % self.host)
            logging.info("ADDER: Exception - %s" % e)


class GetResult():

    def __init__(self, device, host, test_type):
        self.device = device
        self.host = host
        self.test_type = test_type

    def run(self):
        logging.info("ADDER: Getting result from HOST %s @ %s" %
                     (self.host, HOSTS[self.host]))
        while True:
            try:
                payload = {"command": "get_result",
                           "device": self.device,
                           "test_type": self.test_type}
                r = requests.get("http://" + HOSTS[self.host] +
                                 ":" + str(HOST_PORT) +
                                 "/api", params=payload)
                logging.info("ADDER: Assert Get Result response is 200")
                assert(r.status_code == 200)
                if r.content is not "busy":
                    return ("ADDER: HOST %s gives: %s" %
                            (self.host, str(r.json())))
                    break
                else:
                    time.sleep(5)
            except Exception as e:
                logging.info("ADDER: Failed to connect to HOST %s" % self.host)
                logging.info("ADDER: Exception - %s" % e)
                break
