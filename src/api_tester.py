'''
Created on Aug 17, 2016

@author: Mark
'''
import sys
import os
import time
import logging
from collections import OrderedDict
import random
from datetime import datetime
try:
    from utilities import ddx_api
    from utilities.test_video import Video
    from utilities.email_controller import EmailNotifier
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from utilities import ddx_api
    from utilities.test_video import Video
    from utilities.email_controller import EmailNotifier


RESULT = OrderedDict()
T_FORMAT = "%H:%M %d-%m-%Y"


def start_logging():
    location = "/var/log/snakescale-ddxapi/result.log"
    logging.basicConfig(filename=location,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        level=logging.INFO)
    logging.info("==== Started Logging ====")


def stop_logging():
    logging.info("==== Stopped Logging ====")
    time.sleep(1)
    logging.shutdown()


def verification(result, mode, start_time, host, execution):
    end_time = datetime.now()
    if mode.startswith("VIEWONLY"):
        if "FALSE" in result["video"]:
            send_failure(host, mode, start_time,
                         end_time, execution, result)
    elif mode.startswith("SHARED"):
        if mode.endswith("VIEWONLY") or mode.endswith("SHARED"):
            if "FALSE" in result["video"]:
                send_failure(host, mode, start_time,
                             end_time, execution, result)
        elif mode.endswith("EXCLUSIVE") or mode.endswith("PRIVATE"):
            if result["video"] != ["TRUE", "FALSE"]:
                send_failure(host, mode, start_time,
                             end_time, execution, result)
    elif mode.startswith("EXCLUSIVE"):
        if mode.endswith("VIEWONLY"):
            if result["video"] != ["TRUE", "TRUE"]:
                send_failure(host, mode, start_time,
                             end_time, execution, result)
        elif (mode.endswith("SHARED") or
                mode.endswith("EXCLUSIVE") or
                mode.endswith("PRIVATE")):
            if result["video"] != ["TRUE", "FALSE"]:
                send_failure(host, mode, start_time,
                             end_time, execution, result)
    elif mode.startswith("PRIVATE"):
        if result["video"] != ["TRUE", "FALSE"]:
            send_failure(host, mode, start_time,
                         end_time, execution, result)
    if execution % 1000:
        send_update(host, mode, start_time,
                    end_time, execution, result)


def send_update(host, mode, start_time, end_time, execution, result):
    EmailNotifier("ddx30 api",
                  host,
                  mode,
                  start_time.strftime(T_FORMAT),
                  end_time.strftime(T_FORMAT),
                  execution,
                  result).send_ddx_api_update_email()


def send_failure(host, mode, start_time, end_time, execution, result):
    EmailNotifier("ddx30 api",
                  host,
                  mode,
                  start_time.strftime(T_FORMAT),
                  end_time.strftime(T_FORMAT),
                  execution,
                  result).send_bbc_failure_email()


def main():
    global RESULT
    start_time = datetime.now()
    execution = 0
    start_logging()
    consoles = ["6", "7", "8", "9", "10"]
    computers = ["6", "7", "8", "9", "10",
                 "16", "17", "18", "19"]
    modes = ["VIEWONLY/VIEWONLY", "VIEWONLY/SHARED",
             "VIEWONLY/EXCLUSIVE", "VIEWONLY/PRIVATE",
             "SHARED/VIEWONLY", "SHARED/SHARED",
             "SHARED/EXCLUSIVE", "SHARED/PRIVATE",
             "EXCLUSIVE/VIEWONLY", "EXCLUSIVE/SHARED",
             "EXCLUSIVE/EXCLUSIVE", "EXCLUSIVE/PRIVATE",
             "PRIVATE/VIEWONLY", "PRIVATE/SHARED",
             "PRIVATE/EXCLUSIVE", "PRIVATE/PRIVATE"]
    token = ddx_api.login()
    while True:
        for console in consoles:
            for mode in modes:
                execution += 1
                RESULT.clear()
                console_2 = console
                while console_2 == console:
                    console_2 = random.choice(consoles)
                ddx_api.switch(token, console, "20", "VIEWONLY")
                ddx_api.switch(token, console_2, "20", "VIEWONLY")
                time.sleep(2)
                target = random.choice(computers)
                p_mode = mode.split("/")[0]
                s_mode = mode.split("/")[-1]
                ddx_api.switch(token, console, target, p_mode)
                ddx_api.switch(token, console_2, target, s_mode)
                time.sleep(2)
                if target in ["6", "7", "8", "9", "10"]:
                    host = "Ubuntu"
                elif target in ["16", "17", "18", "19"]:
                    host = "Win7"
                multi_view = Video()
                multi_view.set(host, console)
                multi_view.set(host, console_2)
                RESULT.update({"console": console,
                               "computer": target,
                               "mode": mode,
                               "video": multi_view.get()})
                verification(RESULT, mode, start_time, host, execution)

if __name__ == "__main__":
    main()
