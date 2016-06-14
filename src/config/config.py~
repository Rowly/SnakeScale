'''
Created on 11 May 2015

@author: Mark
'''
from collections import OrderedDict
import json

RPIS_LIMIT = None

RPI_PORT = json.load(open("./data.json"))["data"]["rpi_port"]

MBED_LIMIT = None

MBED_ECHO_PORT = json.load(open("./data.json"))["data"]["mbed_port"]

RPIS = OrderedDict()

OSD_MBEDS = OrderedDict()

JOB_MBEDS = OrderedDict()

ALIFS = OrderedDict()


def get_rpis():
    rpis = json.load(open("./data.json"), object_pairs_hook=OrderedDict)
    RPIS.update(rpis["data"]["rpis"])
    return RPIS


def get_mbed_osders():
    osders = json.load(open("./data.json"), object_pairs_hook=OrderedDict)
    OSD_MBEDS.update(osders["data"]["osd_mbeds"])
    return OSD_MBEDS


def get_mbed_jobbers():
    jobbers = json.load(open("./data.json"), object_pairs_hook=OrderedDict)
    JOB_MBEDS.update(jobbers["data"]["job_mbeds"])
    return JOB_MBEDS


def get_alifs():
    alifs = json.load(open("./data.json"), object_pairs_hook=OrderedDict)
    ALIFS.update(alifs["data"]["alifs"])
    return ALIFS


if __name__ == "__main__":
    print("Rpis:")
    print(json.dumps(get_rpis(), indent=2))
    print("Alifs:")
    print(json.dumps(get_alifs(), indent=2))
    print("OSD Mbeds:")
    print(json.dumps(get_mbed_osders(), indent=2))
    print("Job Mbeds:")
    print(json.dumps(get_mbed_jobbers(), indent=2))
    print("Rpi Port: %s" % RPI_PORT)
    print("Mbed Port: %d" % MBED_ECHO_PORT)
