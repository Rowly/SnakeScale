'''
Created on Jun 30, 2016

@author: Mark
'''
import sys
import os
import logging
import datetime
import json
import smtplib
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException
from email.mime.base import MIMEBase
from email import encoders
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from config import config
from utilities import ddx_api


class EmailNotifier():

    def __init__(self, device, host, test_type, start, end,
                 execution, response):
        self.device = device
        self.host = host,
        self.test_type = test_type
        self.start = start
        self.end = end
        self.execution = execution
        self.response = response

    def send_failure_email(self, path):
        token = ddx_api.login(3)
        info = ddx_api.get(token, "systemInfo")
        version = info["firmwareVersion"]
        name = info["description"]
        for endpoint in ["systemInfo", "computers", "consoles",
                         "transmitters", "receivers", "ports",
                         "supplies", "temperatures"]:
            self.get_dump_as_file(token, endpoint, path)
        ddx_api.post(token, "backup", "{}".format(path))
        fail_body = """
               Test for {}
               Unit IP {}
               Unit name {}
               Version {}
               HOST {}
               Using test style {}
               Begun {}
               Ended {}
               Execution number {}
               Response from most recent test:
               {}
               Location of test log /var/log/snakescale-ddx/result.log
               """.format(self.device,
                          config.get_ddx_ut_ip(),
                          name,
                          version,
                          self.host,
                          self.test_type,
                          self.start,
                          self.end,
                          self.execution,
                          self.response)

        commaspace = ", "
        receipients = ["mark.rowlands@adder.com"]
        sender = "ddx30soaktest@example.com"

        outer = MIMEMultipart()
        outer["Subject"] = "DDX30 Failure"
        outer["From"] = sender
        outer["To"] = commaspace.join(receipients)
#         outer.preamble = fail_body

        outer.attach(MIMEText(fail_body))

        directory = "{}/dump/fail".format(path)
        for filename in os.listdir(directory):
            f_path = os.path.join(directory, filename)
            if not os.path.isfile(f_path):
                continue
            ctype, encoding = mimetypes.guess_type(f_path)

            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)
            if maintype == "text":
                fp = open(f_path)
                msg = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(f_path, "rb")
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(fp.read())
                encoders.encode_base64(msg)
            msg.add_header("Content-Disposition",
                           "attachment",
                           filename=filename)
            outer.attach(msg)

        try:
            smtpObj = smtplib.SMTP("hq-mail3.adder.local", 25)
            smtpObj.sendmail(sender, receipients, outer.as_string())
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_failure_email email")

    def send_update_email(self, path):
        token = ddx_api.login(3)
        info = ddx_api.get(token, "systemInfo")
        version = info["firmwareVersion"]
        name = info["description"]
        update_body = """
               Test for {}
               Unit IP {}
               Unit name {}
               Version {}
               HOST {}
               Using test style {}
               Begun {}
               Execution number {}
               Response from most recent test:
               {}
               """.format(self.device,
                          config.get_ddx_ut_ip(),
                          name,
                          version,
                          self.host,
                          self.test_type,
                          self.start,
                          self.execution,
                          self.response)

        commaspace = ", "
        receipients = ["mark.rowlands@adder.com"]

        msg = MIMEText(update_body)

        msg["Subject"] = "DDX30 Status Update"
        msg["From"] = "ddx30soaktest@example.com"
        msg["To"] = commaspace.join(receipients)

        try:
            smtpObj = smtplib.SMTP("hq-mail3.adder.local", 25)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_failure_email email")

    def get_dump_as_file(self, token, endpoint, path):
        content = ddx_api.get(token, endpoint)
        f = os.path.abspath("{}/dump/fail/{}.txt".format(path, endpoint))
        with open(f, "w+") as file:
            file.write(json.dumps(content, indent=4))


if __name__ == "__main__":
    T_FORMAT = "%H:%M %d-%m-%Y"
    start = datetime.datetime.now().strftime(T_FORMAT)
    end = datetime.datetime.now().strftime(T_FORMAT)
    em = EmailNotifier("ddx30", "Ubuntu", "exclusive",
                       start, end, 1, "testing")
    em.send_failure_email("..")
