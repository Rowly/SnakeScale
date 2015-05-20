'''
Created on 8 May 2015

@author: Mark
'''
from root.nested.config import config
from selenium.common.exceptions import TimeoutException
from PIL import Image
import math
import logging
import subprocess

ALIFS = config.get_alifs()


class Capture():

    def __init__(self, alif):
        self.alif = alif

    def run(self):
        logging.info("ADDER: Getting image")
        target = "http://%s" % ALIFS[self.alif]
        try:
            subprocess.Popen("ruby capture.rb http://%s" % target)
        except TimeoutException as e:
            logging.info("ADDER: Timed out, stacktrace: %s" % e)


class ImageCompare():

    def run(self):
        logging.info("ADDER: Comparing images")
        result = "FALSE"
        imageA = Image.open("../imgs/default.png")
        imageB = Image.open("../imgs/capture.png")
        histA = imageA.histogram()
        histB = imageB.histogram()

        diff_squares = [(histA[i] - histB[i]) ** 2 for i in range(len(histA))]
        rms = math.sqrt(sum(diff_squares) / len(histA))
        if rms < 0:
            result = "TRUE"
        return result
