'''
Created on Jun 29, 2016

@author: Mark
'''
import requests
import time


"""
TODO: Put this into Config
"""
IP = "10.10.10.22"


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


def get_system_info(token):
    target = "api/system/systemInfo"
    headers = {"Authorization": "Bearer {}".format(token)}
    r = requests.get("https://{}/{}".format(IP, target),
                     headers=headers,
                     verify=False)
    assert(r.status_code == 200)
    return r.json()

if __name__ == "__main__":
    import json
    token = login()
    info = get_system_info(token)
    print(json.dumps(info, indent=4))
