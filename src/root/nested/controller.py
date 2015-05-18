'''
Created on 27 Apr 2015

@author: Mark
'''
from root.nested.config import config
from root.nested.jobs import pi_jobs
from queue import Queue
import logging
import time
import threading  # @UnusedImport
import argparse

RPIS = config.get_rpis()

ControlQ = Queue()


class Executor():

    def run(self):
        while not ControlQ.empty():
            item = ControlQ.get()
            item.run()


class Jobs():

    def __init__(self, rpi, device):
        self.rpi = rpi
        self.device = device

    def run(self):
        pi_jobs.Notify(self.rpi, self.device)
        pi_jobs.GetResult(self.rpi, self.device)


def logging_start():
    logging.basicConfig(filename="./logs/result.log",
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.INFO)
    logging.info("ADDER: ==== Started Logging ====")


def logging_stop():
    logging.info("ADDER: ==== Stopped Logging ====")
    time.sleep(1)
    logging.shutdown()


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description="Device to test")
        parser.add_argument("device", type=str, help="DDX30, ALIF, CCSPRO4",
                            required=True,
                            choices=["DDX30", "ALIF", "CCSPRO4"])
        parser.add_argument("--pcs", type=int,
                            help="Number of connected Pis", default=20)
        parser.add_argument("--mbeds", type=int,
                            help="Number of connected Mbeds", default=10)
        args = parser.parse_args()
        device = args.device
        config.RPIS_LIMIT = args.pcs
        config.MBED_LIMIT = args.mbeds
        logging_start()
        while True:
            for rpi in RPIS:
                try:
                    item = Jobs(rpi, device)
                    ControlQ.put(item)
                    Executor().run()
                except KeyboardInterrupt:
                    raise
    except KeyboardInterrupt:
        ControlQ.put(None)
        ControlQ.join()
        logging_stop()
