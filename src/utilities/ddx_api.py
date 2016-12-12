'''
Created on Jun 29, 2016

@author: Mark
'''
import sys
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning as irw
import time
try:
    from config import config
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from config import config


requests.packages.urllib3.disable_warnings(irw)  # @UndefinedVariable


def login(retry=0, path=".", unit="dut"):
    if unit == "dut":
        ip = config.get_ddx_ut_ip(path)
    elif unit == "source":
        ip = config.get_ddx_source_ip(path)
    elif unit == "reader":
        ip = config.get_ddx_reader_ip(path)
    target = "api/auth/local"
    payload = {"username": "admin",
               "password": "password"}
    try:
        r = requests.post("https://{}/{}".format(ip, target),
                          params=payload,
                          verify=False)
        assert(r.status_code == 200)
        return r.json()["token"]
    except requests.exceptions.ConnectionError:
        if retry < 3:
            retry += 1
            time.sleep(5)
            login(retry, path)
        else:
            raise


def get(token, endpoint, path=".", target="dut"):
    if target == "dut":
        ip = config.get_ddx_ut_ip(path)
    elif target == "source":
        ip = config.get_ddx_source_ip(path)
    elif target == "reader":
        ip = config.get_ddx_reader_ip(path)

    if endpoint == "systemInfo":
        endpoint = "system/{}".format(endpoint)
    if endpoint == "supplies" or endpoint == "temperatures":
        endpoint = "diagnostics/{}".format(endpoint)

    target = "api/{}".format(endpoint)
    headers = {"Authorization": "Bearer {}".format(token)}
    r = requests.get("https://{}/{}".format(ip, target),
                     headers=headers,
                     verify=False)
    try:
        assert(r.status_code == 200)
    except Exception as e:
        print(target)
        raise e
    return r.json()


def post(token, endpoint, path="."):
    IP = config.get_ddx_ut_ip(path)
    if endpoint == "backup":
        endpoint = "system/{}".format(endpoint)
    target = "api/{}".format(endpoint)
    headers = {"Authorization": "Bearer {}".format(token)}
    r = requests.post("https://{}/{}".format(IP, target),
                      headers=headers,
                      verify=False,
                      stream=True)
    assert(r.status_code == 200)
    f = os.path.abspath("{}/dump/fail/switch.cfg".format(path))
    with open(f, "wb") as fd:
        for chunk in r.iter_content():
            fd.write(chunk)
        fd.close()


def switch(token, console, computer, mode, path="."):
    IP = config.get_ddx_ut_ip(path)
    target = "api/consoles/{}/switch".format(console)
    json = {"computerId": "{}".format(computer),
            "mode": "{}".format(mode)}
    headers = {"Authorization": "Bearer {}".format(token)}
    r = requests.post("https://{}/{}".format(IP, target),
                      headers=headers,
                      json=json,
                      verify=False,
                      stream=True)
    try:
        assert(r.status_code == 204)
    except Exception as e:
        print(target)
        raise e

if __name__ == "__main__":
    import json
    path = ".."
    token = login(0, path)
    info = get(token, "systemInfo", path)
    for console in ["2", "3", "4"]:
        for computer in ["11", "12", "13"]:
            for mode in ["VIEWONLY", "SHARED", "EXCLUSIVE", "PRIVATE", "NONE"]:
                switch(token, console, computer, mode, path)
                endpoint = "consoles/{}".format(console)
                info = get(token, endpoint, path)
                if mode != "NONE":
                    connectedComputer = info["connectedComputer"]
                    currentAccessMode = info["currentAccessMode"]
                    assert(connectedComputer == int(computer))
                    assert(currentAccessMode == mode)
                time.sleep(5)
    for endpoint in ["systemInfo",
                     "computers",
                     "consoles",
                     "transmitters",
                     "receivers",
                     "ports",
                     "supplies",
                     "temperatures",
                     ]:
        info = get(token, endpoint, path)
        print(json.dumps(info, indent=4))
    post(token, "system/backup", path)
