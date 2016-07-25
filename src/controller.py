"""
Created on 27 Apr 2015

@author: Mark

This class runs on the test controller, hence the name.

"""
import sys
import os
from queue import Queue
import logging
import time
import argparse
from datetime import datetime, timedelta
import json
from collections import OrderedDict
try:
    from config import config
    from jobs.pi_jobs import Notify, GetResult
    from utilities.email_controller import EmailNotifier
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from config import config
    from jobs.pi_jobs import Notify, GetResult
    from utilities.email_controller import EmailNotifier

# Get OrderedDict of HOST IP addresses from data.json
PORT = config.get_host_port()
ControlQ = Queue()
T_FORMAT = "%H:%M %d-%m-%Y"
DEBUG = False
RESULT = OrderedDict()


def logging_start(device):
    location = "/var/log/snakescale-{}/result.log".format(device[0:3])
    logging.basicConfig(filename=location,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.INFO)
    logging.info("==== Started Logging ====")


def logging_stop():
    logging.info("==== Stopped Logging ====")
    time.sleep(1)
    logging.shutdown()


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
    Takes in the device that is under test, eg DDX30
    The HOST name of the PC that is to carry out the tests
    Which type of test style is in use
    The resolution of the screen
    The exection number, for failure tracking
    Start time, for failure tracking
    """
    def __init__(self, device, host, test_type, resolution, execution, start):
        self.device = device
        self.host = host
        self.test_type = test_type
        self.resolution = resolution
        self.execution = execution
        self.start = start

    def run(self):
        global RESULT
        """
        First notifies the target HOST PC that it is to
        carry out tests for the device under test.
        """
        Notify(self.device, self.host, self.test_type, self.resolution).run()

        """
        Then fetches the results of the tests from the
        HOST PC.
        """
        RESULT = GetResult().run()

        """
        Result of the most recent test is logged
        """
        logging.info("HOST {} gives:\n {}"
                     .format(self.host, json.dumps(RESULT, indent=4)))

        """
        Record time at the end of each Job
        """
        end_time = datetime.now()

        """
        If 24hours (timedelta(1)) has passed between start_time
        and end_time, send the update email
        """
#         if (self.start - end_time > timedelta(1) or
#                 self.execution % 50 == 0):
        if self.start - end_time > timedelta(1):
            time.sleep(2)
            EmailNotifier(self.device,
                          self.host,
                          self.test_type,
                          self.start.strftime(T_FORMAT),
                          end_time.strftime(T_FORMAT),
                          self.execution,
                          RESULT).send_update_email()
        if test_type == "view":
            if ("TRUE" in RESULT["Single"]["mouse"] or
                    "TRUE" in RESULT["Single"]["keyboard"] or
                    "FALSE" in RESULT["Single"]["video"] or
                    "FALSE" in RESULT["Multi"]["video"]):
                time.sleep(2)
                EmailNotifier(self.device,
                              self.host,
                              self.test_type,
                              self.start.strftime(T_FORMAT),
                              end_time.strftime(T_FORMAT),
                              self.execution,
                              RESULT).send_failure_email()
                sys.exit()
        elif test_type == "shared":
            if ("FALSE" in RESULT["Single"]["mouse"] or
                    "FALSE" in RESULT["Single"]["keyboard"] or
                    "FALSE" in RESULT["Single"]["video"] or
                    "FALSE" in RESULT["Non Contention"]["keyboard"] or
                    "FALSE" in RESULT["Non Contention"]["video"] or
                    "FALSE" in RESULT["Contention"]["keyboard"] or
                    "FALSE" in RESULT["Contention"]["video"]):
                time.sleep(2)
                EmailNotifier(self.device,
                              self.host,
                              self.test_type,
                              self.start.strftime(T_FORMAT),
                              end_time.strftime(T_FORMAT),
                              self.execution,
                              RESULT).send_failure_email()
                sys.exit()
        else:
            if "FALSE" in RESULT:
                time.sleep(2)
                EmailNotifier(self.device,
                              self.host,
                              self.test_type,
                              self.start.strftime(T_FORMAT),
                              end_time.strftime(T_FORMAT),
                              self.execution,
                              RESULT).send_failure_email()
                sys.exit()


def main(device, test_type, resolution):
    logging_start(device)

    start_time = datetime.now()

    """
    TODO: Add in an API call to ensure that all Source Receivers are connected
    through to the HOSTs before tests start
    """
    print(start_time.strftime(T_FORMAT))
    counter = 0
    if device == "ddx30":
        while True:
            for host in ["Win7", "Ubuntu"]:
                counter += 1
                if DEBUG:
                    print(counter)
                    print(host)
                item = Jobs(device, host, test_type,
                            resolution, counter, start_time)
                ControlQ.put(item)
                Executor().run()
                time.sleep(3)
    elif device == "av4pro":
        while True:
            for i in ["1", "2", "3", "4"]:
                counter += 1
                print(counter)
                item = Jobs(device, "av4pro", i, resolution, counter, start_time)
                ControlQ.put(item)
                Executor().run()
                time.sleep(1)


if __name__ == '__main__':
    test_types = ["view", "shared", "exclusive", "private", "conflict", "all"]
    parser = argparse.ArgumentParser(description="Control Server")
    parser.add_argument("device",
                        type=str,
                        help="device under test")
    parser.add_argument("test_type",
                        type=str,
                        choices=test_types,
                        help="Type of test to send_failure_email")
    parser.add_argument("--resolution",
                        type=str,
                        default="1920x1080",
                        help="Resolution of display as 1920x1080")
    parser.add_argument("--debug", dest="debug", action="store_true",
                        help="Show count and HOST name to screen")
    parser.set_defaults(debug=False)

    args = parser.parse_args()
    device = args.device.lower()
    test_type = args.test_type
    resolution = args.resolution
    DEBUG = args.debug
    main(device, test_type, resolution)
