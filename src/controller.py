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
import datetime
from utilities.email_controller import EmailNotifier
sys.path.append(os.path.dirname(__file__))


from config import config
from jobs.pi_jobs import Notify, GetResult

# Get OrderedDict of HOST IP addresses from data.json
PORT = config.get_host_port()
ControlQ = Queue()
T_FORMAT = "%H:%M %d-%m-%Y"


def logging_start():
    logging.basicConfig(filename="/var/log/snakescale-ddx/result.log",
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
    Takes in the IP address of the Raspberry Pi that will be
    carrying out the test and the device type that is under test.
    Device is typically of DDX30 in the initial version.
    """
    def __init__(self, device, host, test_type, resolution, execution, start):
        self.device = device
        self.host = host
        self.test_type = test_type
        self.resolution = resolution
        self.execution = execution
        self.start = start

    def run(self):
        """
        First notifies the target HOST PC that it is to
        carry out tests for the device under test.
        """
        Notify(self.device, self.host, self.test_type, self.resolution).run()

        """
        Then fetches the results of the tests from the
        HOST PCs.
        """
        response = GetResult(self.device, self.host, self.test_type).run()

        """
        Result of the most recent test is logged
        """
        logging.info("{}".format(response))

        """
        A place holder to test the email sending system
        """
        end_time = datetime.datetime.now().strftime(T_FORMAT)

        if self.execution % 1000 == 0:
            time.sleep(2)
            EmailNotifier(self.device,
                          self.test_type,
                          self.start,
                          end_time,
                          self.execution,
                          response).send_update_email()
        if test_type == "view":
            if "TRUE" in response:
                time.sleep(2)
                EmailNotifier(self.device,
                              self.test_type,
                              self.start,
                              end_time,
                              self.execution,
                              response).send_failure_email()
                sys.exit()
        else:
            if "FALSE" in response:
                time.sleep(2)
                EmailNotifier(self.device,
                              self.test_type,
                              self.start,
                              end_time,
                              self.execution,
                              response).send_failure_email()
                sys.exit()


def main(device, hosts, test_type, resolution):
    logging_start()
    config.RPIS_LIMIT = hosts

    start_time = datetime.datetime.now().strftime(T_FORMAT)

    """
    TODO: Add in an API call to ensure that all receivers are connected
    through to the hosts before tests start
    """
    print(start_time)
    counter = 0
    if device == "ddx30":
        while True:
            counter += 1
            print(counter)
            item = Jobs(device, "1", test_type, resolution, counter, start_time)
            ControlQ.put(item)
            Executor().run()
            time.sleep(1)
    elif device == "av4pro":
        while True:
            for i in ["1", "2", "3", "4"]:
                counter += 1
                print(counter)
                item = Jobs(device, "1", i, resolution, counter, start_time)
                ControlQ.put(item)
                Executor().run()
                time.sleep(1)


if __name__ == '__main__':
    test_types = ["view", "shared", "exclusive", "private", "conflict", "all"]
    parser = argparse.ArgumentParser(description="Control Server")
    parser.add_argument("device",
                        type=str,
                        help="device under test")
    parser.add_argument("hosts",
                        type=str,
                        help="Number of Host PCS")
    parser.add_argument("test_type",
                        type=str,
                        choices=test_types,
                        help="Type of test to send_failure_email")
    parser.add_argument("resolution",
                        type=str,
                        help="Resolution of display as 1920x1080")
    args = parser.parse_args()
    device = args.device.lower()
    hosts = args.hosts
    test_type = args.test_type
    resolution = args.resolution
    main(device, hosts, test_type, resolution)
