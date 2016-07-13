'''
Created on 29 Apr 2015

@author: Mark
'''
import os
import logging
import subprocess
import random
import json

TEST_STRING = "abcdefghijklmnopqrstuvwxyz"


def key_b(path="./dump/test.txt"):
    result = "FALSE"
    try:
        f = os.path.abspath(path)
        data = [line.strip() for line in open(f)]
        if TEST_STRING in set(data):
            result = "TRUE"
    except IOError as e:
        logging.info("Could not find test file.")
        logging.info("{}".format(e))
    return result


def info():
    fetched = subprocess.check_output("lsusb", shell=True)
    devices = [each for each in str(fetched, "UTF-8").split("\n")]
    return devices


def mouse(path="./dump/test.txt"):
    result = {"right": "FALSE",
              "left": "FALSE",
              "no": "FALSE"}
    try:
        f = os.path.abspath(path)
        data = [line.strip() for line in open(f)]
        rights = [line for line in data if line.startswith("Right")]
        lefts = [line for line in data if line.startswith("Left")]
        nos = [line for line in data if line.startswith("No")]

        try:
            sample_rights = random.sample(range(0, len(rights)), 2)
            r1 = rights[sample_rights[0]]
            r2 = rights[sample_rights[-1]]
            if r1 != r2:
                result["right"] = "TRUE"
        except ValueError:
            pass

        try:
            sample_lefts = random.sample(range(0, len(lefts)), 2)
            l1 = lefts[sample_lefts[0]]
            l2 = lefts[sample_lefts[-1]]
            if l1 != l2:
                result["left"] = "TRUE"
        except ValueError:
            pass

        try:
            sample_nos = random.sample(range(0, len(nos)), 2)
            n1 = nos[sample_nos[0]]
            n2 = nos[sample_nos[-1]]
            if n1 != n2:
                result["no"] = "TRUE"
        except ValueError:
            pass
    except IOError as e:
        logging.info("Could not find test file")
        logging.info("{}".format(e))
    return result


if __name__ == "__main__":
    data = json.dumps({"mouse": mouse("../dump/test.txt"),
                       "keyb": key_b("../dump/test.txt")}, indent=4)
    print(data)
