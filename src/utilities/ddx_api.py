'''
Created on Jun 29, 2016

@author: Mark
'''
import requests
import time
from config import config


# IP = config.get_dut_ip("../config/data.json")
IP = config.get_dut_ip()


def login(retry=0):
    target = "api/auth/local"
    payload = {"username": "admin",
               "password": "password"}
    try:
        r = requests.post("https://{}/{}".format(IP, target),
                          params=payload,
                          verify=False)
        assert(r.status_code == 200)
        return r.json()["token"]
    except requests.exceptions.ConnectionError:
        if retry < 3:
            retry += 1
            time.sleep(5)
            login(retry)
        else:
            raise


def get(token, endpoint):
    if endpoint == "systemInfo":
        endpoint = "system/{}".format(endpoint)
    if endpoint == "supplies" or endpoint == "temperatures":
        endpoint = "diagnostics/{}".format(endpoint)
    target = "api/{}".format(endpoint)
    headers = {"Authorization": "Bearer {}".format(token)}
    r = requests.get("https://{}/{}".format(IP, target),
                     headers=headers,
                     verify=False)
    try:
        assert(r.status_code == 200)
    except Exception as e:
        print(endpoint)
        raise e
    return r.json()


def post(token, endpoint, path="."):
    if endpoint == "backup":
        endpoint = "system/{}".format(endpoint)
    target = "api/{}".format(endpoint)
    headers = {"Authorization": "Bearer {}".format(token)}
    r = requests.post("https://{}/{}".format(IP, target),
                      headers=headers,
                      verify=False,
                      stream=True)
    assert(r.status_code == 200)
    with open("{}/dump/fail/switch.cfg".format(path), "wb") as fd:
        for chunk in r.iter_content():
            fd.write(chunk)
        fd.close()


if __name__ == "__main__":
    import json
    token = login()
    for endpoint in ["systemInfo",
#                      "computers",
#                      "consoles",
#                      "transmitters",
#                     "receivers",
#                      "ports",
#                      "supplies",
#                      "temperatures",
                     ]:
        info = get(token, endpoint)
        print(json.dumps(info, indent=4))
#     post(token, "system/backup", "..")
