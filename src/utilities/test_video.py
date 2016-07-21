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

RESULT = []


class Video():

    def set(self, host, target, path="."):
        global RESULT

        if host == "Ubuntu":
            port = "21"
        elif host == "Win7":
            port = "22"
        token = ddx_api.login(0, path, "source")
        source = ddx_api.get(token,
                             "transmitters/{}".format(port),
                             path,
                             "source")

        token = ddx_api.login(0, path, "reader")
        reader = ddx_api.get(token,
                             "transmitters/{}".format(target),
                             path,
                             "reader")

        if (source["height"] == reader["height"] and
                source["width"] == reader["width"]):
            RESULT.append("TRUE")
            print("TRUE")
        else:
            RESULT.append("FALSE")
            print("FALSE")

    def get(self):
        global RESULT
        r = RESULT.copy()
        RESULT.clear()
        return r


if __name__ == "__main__":
    one = Video()
    one.set("Ubuntu", "1", "..")
    print(one.get())
    two = Video()
    two.set("Ubuntu", "1", "..")
    two.set("Ubuntu", "2", "..")
    print(two.get())
