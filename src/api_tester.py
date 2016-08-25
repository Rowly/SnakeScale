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
import json
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
#     if mode.startswith("VIEWONLY"):
#         # Only test for false due to fall back to highest possible
#         # ie if View in place can't connect PRIVATE on 2nd so
#         # connects as exclusive
#         if "FALSE" in result["video"]:
#             failure(host, mode, start_time,
#                     end_time, execution, result)
#     elif mode.startswith("SHARED"):
#         if mode.endswith("VIEWONLY") or mode.endswith("SHARED"):
#             if "FALSE" in result["video"]:
#                 failure(host, mode, start_time,
#                         end_time, execution, result)
#         elif mode.endswith("EXCLUSIVE") or mode.endswith("PRIVATE"):
#             if result["video"] != ["TRUE", "FALSE"]:
#                 failure(host, mode, start_time,
#                         end_time, execution, result)
#     elif mode.startswith("EXCLUSIVE"):
#         if mode.endswith("VIEWONLY"):
#             if result["video"] != ["TRUE", "TRUE"]:
#                 failure(host, mode, start_time,
#                         end_time, execution, result)
#         elif (mode.endswith("SHARED") or
#                 mode.endswith("EXCLUSIVE") or
#                 mode.endswith("PRIVATE")):
#             if result["video"] != ["TRUE", "FALSE"]:
#                 failure(host, mode, start_time,
#                         end_time, execution, result)
    if mode.startswith("PRIVATE"):
        if result["video"] != ["TRUE", "FALSE"]:
            failure(host, mode, start_time,
                    end_time, execution, result)
    elif not mode.startswith("PRIVATE"):
        if "FALSE" in result["video"]:
            failure(host, mode, start_time,
                    end_time, execution, result)

    if execution % 1000 == 0:
        update(host, mode, start_time,
               end_time, execution, result)


def update(host, mode, start_time, end_time, execution, result):
    EmailNotifier("ddx30 api",
                  host,
                  mode,
                  start_time.strftime(T_FORMAT),
                  end_time.strftime(T_FORMAT),
                  execution,
                  result).send_ddx_api_update_email()


def failure(host, mode, start_time, end_time, execution, result):
    EmailNotifier("ddx30 api",
                  host,
                  mode,
                  start_time.strftime(T_FORMAT),
                  end_time.strftime(T_FORMAT),
                  execution,
                  result).send_ddx_api_failure_email()
    stop_logging()
    sys.exit()


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
    for console in consoles:
        ddx_api.switch(token, console, "1", "NONE")
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
                time.sleep(5)
                target = random.choice(computers)
                p_mode = mode.split("/")[0]
                s_mode = mode.split("/")[-1]
                ddx_api.switch(token, console, target, p_mode)
                ddx_api.switch(token, console_2, target, s_mode)
                time.sleep(5)
                if target in ["6", "7", "8", "9", "10"]:
                    host = "Ubuntu"
                elif target in ["16", "17", "18", "19"]:
                    host = "Win7"
                multi_view = Video()
                multi_view.set(host, console)
                multi_view.set(host, console_2)
                RESULT.update({"console 1": console,
                               "console 2": console_2,
                               "computer": target,
                               "mode": mode,
                               "video": multi_view.get()})
                logging.info("\n{}".format(json.dumps(RESULT, indent=2)))
                verification(RESULT, mode, start_time, host, execution)

if __name__ == "__main__":
    main()
