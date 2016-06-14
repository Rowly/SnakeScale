"""
Created on 27 Apr 2015

@author: Mark

This class runs on the test controller, hence the name.
It takes upto 3 arguments, 1 required and the other 2 optional
as they have default values.

"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import config
from jobs import pi_jobs
from queue import Queue
import logging
import time
import threading  # @UnusedImport
import argparse

# Get OrderedDict of Raspberry Pi IP addresses from data.json
RPIS = config.get_rpis()

ControlQ = Queue()


class Executor():
    """
    Each item is a Jobs() instance.
    Takes an item from the queue and executes it.
    """
    def run(self):
        while not ControlQ.empty():
            item = ControlQ.get()
            item.run()


class Jobs():
    """
    Takes in the IP address of the Raspberry Pi that will be
    carrying out the test and the device type that is under test.
    Device is typically of DDX30 in the initial version.
    """
    def __init__(self, rpi, device):
        self.rpi = rpi
        self.device = device

    def run(self):
        """
        First notifies the target Raspberry Pi that it is to
        carry out tests for the device under tests.

        Then fetches the results of the tests from the
        Raspberry Pis.
        """
        pi_jobs.Notify(self.rpi, self.device).run()
        pi_jobs.GetResult(self.rpi, self.device).run()


def logging_start():
    """
    Inclusion of ADDER prefix to enable quick grep'ing of results
    """
    logging.basicConfig(filename="/var/log/snakescale-ddx/result.log",
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.INFO)
    logging.info("ADDER: ==== Started Logging ====")


def logging_stop():
    """
    Inclusion of ADDER prefix to enable quick grep'ing of results
    """
    logging.info("ADDER: ==== Stopped Logging ====")
    time.sleep(1)
    logging.shutdown()


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Device to test")
        parser.add_argument("device", type=str, help="DDX30, ALIF, CCSPRO4",
                            choices=["DDX30", "ALIF", "CCSPRO4"])
        parser.add_argument("--pcs", type=int,
                            help="Number of connected Pis", default=23)
        parser.add_argument("--mbeds", type=int,
                            help="Number of connected Mbed pairs", default=7)
        args = parser.parse_args()
        device = args.device
        config.RPIS_LIMIT = args.pcs
        config.MBED_LIMIT = args.mbeds
        logging_start()
        
        item = Jobs("1", device)
        ControlQ.put(item)
        Executor().run()
    except KeyboardInterrupt:
        ControlQ.put(None)
        ControlQ.join()
        logging_stop()
