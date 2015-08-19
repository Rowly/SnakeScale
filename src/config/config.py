'''
Created on 11 May 2015

@author: Mark
'''
from collections import OrderedDict
import json

DEFAULT_PATH = "./config/data.json"

RPIS_LIMIT = None

RPI_PORT = None

MBED_LIMIT = None

MBED_ECHO_PORT = None

RPIS = OrderedDict()

OSD_MBEDS = OrderedDict()

JOB_MBEDS = OrderedDict()

ALIFS = OrderedDict()


def get_rpis_port(path=DEFAULT_PATH):
    return json.load(open(path))["data"]["rpi_port"]

def get_rpis(path=DEFAULT_PATH):
    rpis = json.load(open(path), object_pairs_hook=OrderedDict)
    RPIS.update(rpis["data"]["rpis"])
    return RPIS

def get_mbed_echo_port(path=DEFAULT_PATH):
    return json.load(open(path))["data"]["mbed_port"]

def get_mbed_osders(path=DEFAULT_PATH):
    osders = json.load(open(path), object_pairs_hook=OrderedDict)
    OSD_MBEDS.update(osders["data"]["osd_mbeds"])
    return OSD_MBEDS
    
def get_mbed_jobbers(path=DEFAULT_PATH):
    jobbers = json.load(open(path), object_pairs_hook=OrderedDict)
    JOB_MBEDS.update(jobbers["data"]["job_mbeds"])
    return JOB_MBEDS

def get_alifs(path=DEFAULT_PATH):
    alifs = json.load(open(path), object_pairs_hook=OrderedDict)
    ALIFS.update(alifs["data"]["alifs"])
    return ALIFS


if __name__ == "__main__":
    print("Rpis:")
    print(json.dumps(get_rpis("data.json"), indent=2))
    print("Alifs:")
    print(json.dumps(get_alifs("data.json"), indent=2))
    print("OSD Mbeds:")
    print(json.dumps(get_mbed_osders("data.json"), indent=2))
    print("Job Mbeds:")
    print(json.dumps(get_mbed_jobbers("data.json"), indent=2))
    print("Rpi Port: ")
    print(json.dumps(get_rpis_port("data.json")))
    print("Mbed Port: ")
    print(json.dumps(get_mbed_echo_port("data.json")))
