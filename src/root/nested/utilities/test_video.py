'''
Created on 8 May 2015

@author: Mark
'''
from root.nested.config import config
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PIL import Image
import math
import logging
import sys

ALIFS = config.get_alifs()


class Capture():

    def __init__(self, alif):
        self.alif = alif

    def run(self):
        logging.info("ADDER: Getting image")
        target = "http://%s" % ALIFS[self.alif]
        if sys.platform == "win32":
            path = "phantomjs.exe"
        elif sys.platform == "linux2":
            path = "/var/bin/phantomjs"
        try:
            driver = webdriver.PhantomJS(executable_path=path)
            wait = WebDriverWait(driver, 30)
            driver.get(target)
            button = By.CSS_SELECTOR, "#refresh_thumbnail"
            wait.until(EC.presence_of_element_located(button)).click()
            image = By.CSS_SELECTOR, "#right > div > a:nth-child(5)"
            wait.until(EC.element_to_be_clickable(image)).click()
            driver.save_screenshot("../imgs/capture.png")
        except TimeoutException as e:
            logging.info("ADDER: Timed out, stacktrace: %s" % e)
        finally:
            driver.quit()


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
