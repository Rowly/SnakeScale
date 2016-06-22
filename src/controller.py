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
from smtplib import SMTPException
sys.path.append(os.path.dirname(__file__))


from config import config
from jobs.pi_jobs import Notify, GetResult

# Get OrderedDict of HOST IP addresses from data.json
PORT = config.get_host_port()
ControlQ = Queue()


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
    def __init__(self, device, host, test_type, execution):
        self.device = device
        self.host = host
        self.test_type = test_type
        self.execution = execution

    def run(self):
        """
        First notifies the target Raspberry Pi that it is to
        carry out tests for the device under tests.

        Then fetches the results of the tests from the
        Raspberry Pis.
        """
        Notify(self.device, self.host, self.test_type).run()
        response = GetResult(self.device, self.host, self.test_type).run()
        logging.info("{}".format(response))
        if "FALSE" in response:
            time.sleep(2)
            body = """
                   Test for {}
                   Using test style {}
                   Execution number {}
                   Response from most recent test:
                   {}
                   """.format(self.device,
                              self.test_type,
                              self.execution,
                              response)
            EmailNotifier(body).run()
            sys.exit()


class EmailNotifier():

    def __init__(self, body):
        self.body = body

    def run(self):
        import smtplib
        from email.mime.text import MIMEText

        commaspace = ", "
        receipients = ["mark.rowlands@adder.com"]

        try:
            with open("./dump/msg.txt", "w+") as file:
                file.write(self.body)
        except FileNotFoundError:
            with open("./dump/msg.txt", "a") as file:
                file.write(self.body)

        with open("./dump/msg.txt") as file:
            msg = MIMEText(file.read())
        msg["Subject"] = "DDX30 Failure"
        msg["From"] = "ddx30soaktest@example.com"
        msg["To"] = commaspace.join(receipients)

        try:
            smtpObj = smtplib.SMTP("hq-mail3.adder.local", 25)
            smtpObj.send_message(msg)
            smtpObj.quit()
            print("Sent email")
        except SMTPException:
            print("Something went wrong")


def main(device, hosts, test_type):
    logging_start()
    device = device
    config.RPIS_LIMIT = hosts

    counter = 0
    while True:
        counter += 1
        print(counter)
        item = Jobs(device, "1", test_type, counter)
        ControlQ.put(item)
        Executor().run()
        time.sleep(1)


if __name__ == '__main__':
    test_types = ["view", "shared", "exclusive", "private", "conflict", "all"]
    parser = argparse.ArgumentParser(description="Control Server")
    parser.add_argument("device", type=str, help="device under test")
    parser.add_argument("hosts", type=str, help="Number of Host PCS")
    parser.add_argument("test_type", type=str, choices=test_types, help="Type of test to run")
    args = parser.parse_args()
    device = args.device.lower()
    hosts = args.hosts
    test_type = args.test_type
    main(device, hosts, test_type)
