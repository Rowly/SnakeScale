'''
Created on 27 Apr 2015

@author: Mark
'''
import requests
import logging
import time
try:
    from config import config
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from config import config


HOST_PORT = config.get_host_port()
HOSTS = config.get_hosts()


class Notify():

    def __init__(self, device, host, test_type, resolution):
        self.device = device
        self.host = host
        self.test_type = test_type
        self.resolution = resolution

    def run(self):
        logging.info("Prepped HOST {} @ {} to run test"
                     .format(self.host, HOSTS[self.host]))
        try:
            payload = {"command": "notify",
                       "device": self.device,
                       "host": self.host,
                       "test_type": self.test_type,
                       "resolution": self.resolution}
            r = requests.get("http://" + HOSTS[self.host] +
                             ":" + str(HOST_PORT) +
                             "/api", params=payload)
            logging.info("Assert Notify response is 200")
            assert(r.status_code == 200)
        except Exception as e:
            logging.info("Failed to connect to HOST {}"
                         .format(self.host))
            logging.info("Exception - {}".format(e))


class GetResult():

    def __init__(self, device, host):
        self.device = device
        self.host = host

    def run(self):
        logging.info("Getting result from HOST {} @ {}"
                     .format(self.host, HOSTS[self.host]))
        while True:
            try:
                payload = {"command": "get_result"}
                r = requests.get("http://" + HOSTS[self.host] +
                                 ":" + str(HOST_PORT) +
                                 "/api", params=payload)
                logging.info("Assert Get Result response is 200")
                assert(r.status_code == 200)
                if r.content is not "busy":
                    return r.json()
                    break
                else:
                    time.sleep(5)
            except Exception as e:
                logging.info("Failed to connect to HOST {}"
                             .format(self.host))
                logging.info("Exception - {}".format(e))
                break
