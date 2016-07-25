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


def get_host_port(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["host_port"]


def get_hosts(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    hosts = json.load(open(f), object_pairs_hook=OrderedDict)
    HOSTS.update(hosts["data"]["hosts"])
    return HOSTS


def get_mbed_echo_port(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["mbed_port"]


def get_mbed_osders(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    osders = json.load(open(f), object_pairs_hook=OrderedDict)
    OSD_MBEDS.update(osders["data"]["osd_mbeds"])
    return OSD_MBEDS


def get_mbed_jobbers(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    jobbers = json.load(open(f), object_pairs_hook=OrderedDict)
    JOB_MBEDS.update(jobbers["data"]["job_mbeds"])
    return JOB_MBEDS


def get_ddx_ut_ip(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["dut_ip"]


def get_ddx_source_ip(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["d_source_ip"]


def get_ddx_reader_ip(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["d_reader_ip"]


def get_smtp_server_ip(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["smtp_server"]


def get_email_recipients(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["email_recipients"]


def get_av4pro_mbed_ip(path="."):
    path = "{}/config/data.json".format(path)
    f = os.path.abspath(path)
    return json.load(open(f))["data"]["av4pro_mbed"]


if __name__ == "__main__":
    print("Rpis:")
    print(json.dumps(get_hosts(".."), indent=2))
    print("OSD Mbeds:")
    print(json.dumps(get_mbed_osders(".."), indent=2))
    print("Job Mbeds:")
    print(json.dumps(get_mbed_jobbers(".."), indent=2))
    print("Rpi Port: ")
    print(json.dumps(get_host_port("..")))
    print("Mbed Port: ")
    print(json.dumps(get_mbed_echo_port("..")))
    print("Device Under Test IP: ")
    print(json.dumps(get_ddx_ut_ip("..")))
    print("Device Source IP: ")
    print(json.dumps(get_ddx_source_ip("..")))
    print("Device Reader Test IP: ")
    print(json.dumps(get_ddx_reader_ip("..")))
    print("SMTP Server IP:")
    print(json.dumps(get_smtp_server_ip("..")))
    print("Email Recipients")
    print(json.dumps(get_email_recipients("..")))
    print("AV4PRO Details")
    print(json.dumps(get_av4pro_mbed_ip("..")))
