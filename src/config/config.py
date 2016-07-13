'''
Created on 11 May 2015

@author: Mark
'''
import json
from collections import OrderedDict
import os

RPIS_LIMIT = None

HOST_PORT = None

MBED_ECHO_PORT = None

HOSTS = OrderedDict()

OSD_MBEDS = OrderedDict()

JOB_MBEDS = OrderedDict()

ALIFS = OrderedDict()


def get_host_port(path="./config/data.json"):
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["host_port"]


def get_hosts(path="./config/data.json"):
    f = os.path.abspath(path)
    hosts = json.load(open(f), object_pairs_hook=OrderedDict)
    HOSTS.update(hosts["data"]["hosts"])
    return HOSTS


def get_mbed_echo_port(path="./config/data.json"):
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["mbed_port"]


def get_mbed_osders(path="./config/data.json"):
    f = os.path.abspath(path)
    osders = json.load(open(f), object_pairs_hook=OrderedDict)
    OSD_MBEDS.update(osders["data"]["osd_mbeds"])
    return OSD_MBEDS


def get_mbed_jobbers(path="./config/data.json"):
    f = os.path.abspath(path)
    jobbers = json.load(open(f), object_pairs_hook=OrderedDict)
    JOB_MBEDS.update(jobbers["data"]["job_mbeds"])
    return JOB_MBEDS


def get_alifs(path="./config/data.json"):
    f = os.path.abspath(path)
    alifs = json.load(open(f), object_pairs_hook=OrderedDict)
    ALIFS.update(alifs["data"]["alifs"])
    return ALIFS


def get_ddx_ut_ip(path="./config/data.json"):
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["dut_ip"]


def get_ddx_source_ip(path="./config/data.json"):
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["d_source_ip"]


def get_ddx_reader_ip(path="./config/data.json"):
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["d_reader_ip"]


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
    print("Device Under Test IP: ")
    print(json.dumps(get_ddx_ut_ip("data.json")))
    print("Device Source IP: ")
    print(json.dumps(get_ddx_source_ip("data.json")))
    print("Device Reader Test IP: ")
    print(json.dumps(get_ddx_reader_ip("data.json")))
