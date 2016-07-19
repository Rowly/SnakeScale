'''
Created on 8 May 2015

@author: Mark
'''
import sys
import os
try:
    from utilities import ddx_api
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from utilities import ddx_api

RESULT = False


class Video():

    def __init__(self, host, target):
        self.host = host
        self.target = target

    def set_response(self, path="."):
        global RESULT

        if self.host == "Ubuntu":
            port = "21"
        elif self.host == "Win7":
            port = "22"
        token = ddx_api.login(0, path, "source")
        source = ddx_api.get(token,
                             "transmitters/{}".format(port),
                             path,
                             "source")

        token = ddx_api.login(0, path, "reader")
        reader = ddx_api.get(token,
                             "transmitters/{}".format(self.target),
                             path,
                             "reader")

        if source["height"] == reader["height"] and source["width"] == reader["width"]:
            RESULT = True

    def get_response(self):
        global RESULT
        return RESULT


if __name__ == "__main__":
    v = Video("Ubuntu", "1")
    v.set_response("..")
    print(v.get_response())
