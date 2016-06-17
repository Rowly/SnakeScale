'''
Created on 11 May 2015

@author: Mark
'''
from collections import OrderedDict
import json

RPIS_LIMIT = None

HOST_PORT = None

MBED_ECHO_PORT = None

HOSTS = OrderedDict()

OSD_MBEDS = OrderedDict()

JOB_MBEDS = OrderedDict()

ALIFS = OrderedDict()


def get_host_port(path="./config/data.json"):
    return json.load(open(path))["data"]["host_port"]


def get_hosts(path="./config/data.json"):
    hosts = json.load(open(path), object_pairs_hook=OrderedDict)
    HOSTS.update(hosts["data"]["hosts"])
    return HOSTS


def get_mbed_echo_port(path="./config/data.json"):
    return json.load(open(path))["data"]["mbed_port"]


def get_mbed_osders(path="./config/data.json"):
    osders = json.load(open(path), object_pairs_hook=OrderedDict)
    OSD_MBEDS.update(osders["data"]["osd_mbeds"])
    return OSD_MBEDS


def get_mbed_jobbers(path="./config/data.json"):
    jobbers = json.load(open(path), object_pairs_hook=OrderedDict)
    JOB_MBEDS.update(jobbers["data"]["job_mbeds"])
    return JOB_MBEDS


def get_alifs(path="./config/data.json"):
    alifs = json.load(open(path), object_pairs_hook=OrderedDict)
    ALIFS.update(alifs["data"]["alifs"])
    return ALIFS


if __name__ == "__main__":
    print("Rpis:")
    print(json.dumps(get_hosts("data.json"), indent=2))
    print("Alifs:")
    print(json.dumps(get_alifs("data.json"), indent=2))
    print("OSD Mbeds:")
    print(json.dumps(get_mbed_osders("data.json"), indent=2))
    print("Job Mbeds:")
    print(json.dumps(get_mbed_jobbers("data.json"), indent=2))
    print("Rpi Port: ")
    print(json.dumps(get_host_port("data.json")))
    print("Mbed Port: ")
    print(json.dumps(get_mbed_echo_port("data.json")))
