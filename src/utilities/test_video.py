'''
Created on 8 May 2015

@author: Mark
'''
from config import config
from PIL import Image
import math
import logging
import requests

ALIFS = config.get_alifs()


class Capture():

    def __init__(self, alif):
        self.alif = alif

    def run(self, path="./imgs/capture.png"):
        logging.info("Getting image")
        target = "http://%s" % ALIFS[self.alif]
        try:
            response = requests.get(target +
                                    "/cgi-bin/show?page=screencapture0.html")
            if response.status_code == 200:
                f = open(path, 'wb')
                f.write(response.content)
                f.close()
        except Exception as e:
            logging.info("Error, stacktrace: %s" % e)


class ImageCompare():

    def run(self,
            cap_path="./imgs/capture.png",
            def_path="./imgs/default.png"):
        logging.info("ADDER: Comparing images")
        result = "FALSE"
        imageA = Image.open(def_path)
        imageB = Image.open(cap_path)
        histA = imageA.histogram()
        histB = imageB.histogram()

        diff_squares = [(histA[i] - histB[i]) ** 2 for i in range(len(histA))]
        rms = math.sqrt(sum(diff_squares) / len(histA))
        if rms < 0:
            result = "TRUE"
        return result


if __name__ == "__main__":
    for i in range(1, 7):
        Capture(str(i)).run("../imges/capture.png")
        r = ImageCompare(str(i)).run("../imges/capture.png",
                                     "../imges/default.png")
        print(r)
