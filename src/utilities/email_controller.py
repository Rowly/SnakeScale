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
try:
    from config import config
    from utilities import ddx_api
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from config import config
    from utilities import ddx_api


class EmailNotifier():

    def __init__(self, device, host, test_type, start, end,
                 execution, response):
        self.device = device
        self.host = host,
        self.test_type = test_type.upper()
        self.start = start
        self.end = end
        self.execution = execution
        self.response = response
        self.recipients = config.get_email_recipients(".")

    def send_bbc_failure_email(self, path="."):
        fail_body = """
               Test for {}
               Begun {}
               Ended {}
               Execution number {}
               HOST {}
               Response from most recent test:
               {}
               Location of test log:
               vnc to 192.168.42.179
               directory /var/log/snakescale-bbc/result.log
               """.format(self.device,
                          self.start,
                          self.end,
                          self.execution,
                          self.host,
                          json.dumps(self.response, indent=4))
        commaspace = ", "

        msg = MIMEText(fail_body)

        msg["Subject"] = "BBC Failure"
        msg["From"] = "ddx30soaktest@example.com"
        msg["To"] = commaspace.join(self.recipients)

        try:
            smtp_ip = config.get_smtp_server_ip(path)
            smtpObj = smtplib.SMTP(smtp_ip, 25)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_bbc_failure_email email")

    def send_bbc_update_email(self, path="."):
        fail_body = """
               Test for {}
               Begun {}
               Ended {}
               Execution number {}
               HOST {}
               Response from most recent test:
               {}
               Location of test log:
               vnc to 192.168.42.179
               directory /var/log/snakescale-av4/result.log
               """.format(self.device,
                          self.start,
                          self.end,
                          self.execution,
                          self.host,
                          json.dumps(self.response, indent=4))
        commaspace = ", "

        msg = MIMEText(fail_body)

        msg["Subject"] = "BBC Update Email"
        msg["From"] = "ddx30soaktest@example.com"
        msg["To"] = commaspace.join(self.recipients)

        try:
            smtp_ip = config.get_smtp_server_ip(path)
            smtpObj = smtplib.SMTP(smtp_ip, 25)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_bbc_update_email email")

    def send_av4pro_failure_email(self, path="."):
        fail_body = """
               Test for {}
               Begun {}
               Ended {}
               Execution number {}
               Response from most recent test:
               {}
               Location of test log:
               vnc to 192.168.42.179
               directory /var/log/snakescale-av4/result.log
               """.format(self.device,
                          self.start,
                          self.end,
                          self.execution,
                          json.dumps(self.response, indent=4))
        commaspace = ", "

        msg = MIMEText(fail_body)

        msg["Subject"] = "AV4Pro Failure"
        msg["From"] = "ddx30soaktest@example.com"
        msg["To"] = commaspace.join(self.recipients)

        try:
            smtp_ip = config.get_smtp_server_ip(path)
            smtpObj = smtplib.SMTP(smtp_ip, 25)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_av4pro_failure_email email")

    def send_av4pro_update_email(self, path="."):
        fail_body = """
               Test for {}
               Begun {}
               Ended {}
               Execution number {}
               Response from most recent test:
               {}
               Location of test log:
               vnc to 192.168.42.179
               directory /var/log/snakescale-av4/result.log
               """.format(self.device,
                          self.start,
                          self.end,
                          self.execution,
                          json.dumps(self.response, indent=4))
        commaspace = ", "

        msg = MIMEText(fail_body)

        msg["Subject"] = "AV4Pro Update Email"
        msg["From"] = "ddx30soaktest@example.com"
        msg["To"] = commaspace.join(self.recipients)

        try:
            smtp_ip = config.get_smtp_server_ip(path)
            smtpObj = smtplib.SMTP(smtp_ip, 25)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_av4pro_update_email email")

    def send_ddx_failure_email(self, path="."):
        token = ddx_api.login(3, path)
        info = ddx_api.get(token, "systemInfo", path)
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
               Location of test log:
               vnc to 192.168.42.179
               directory /var/log/snakescale-ddx/result.log
               """.format(self.device,
                          config.get_ddx_ut_ip(path),
                          name,
                          version,
                          self.host,
                          self.test_type,
                          self.start,
                          self.end,
                          self.execution,
                          json.dumps(self.response, indent=4))

        commaspace = ", "
        sender = "ddx30soaktest@example.com"

        outer = MIMEMultipart()
        outer["Subject"] = "DDX30 Failure"
        outer["From"] = sender
        outer["To"] = commaspace.join(self.recipients)

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
            smtp_ip = config.get_smtp_server_ip(path)
            smtpObj = smtplib.SMTP(smtp_ip, 25)
            smtpObj.sendmail(sender, self.recipients, outer.as_string())
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_ddx_failure_email email")

    def send_ddx_update_email(self, path="."):
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

        msg = MIMEText(update_body)

        msg["Subject"] = "DDX30 Status Update"
        msg["From"] = "ddx30soaktest@example.com"
        msg["To"] = commaspace.join(self.recipients)

        try:
            smtp_ip = config.get_smtp_server_ip(path)
            smtpObj = smtplib.SMTP(smtp_ip, 25)
            smtpObj.send_message(msg)
            smtpObj.quit()
        except SMTPException:
            logging.info("Failed to send send_ddx_update_email email")

    def get_dump_as_file(self, token, endpoint, path):
        content = ddx_api.get(token, endpoint, path)
        f = os.path.abspath("{}/dump/fail/{}.txt".format(path, endpoint))
        with open(f, "w+") as file:
            file.write(json.dumps(content, indent=4))


if __name__ == "__main__":
    T_FORMAT = "%H:%M %d-%m-%Y"
    start = datetime.datetime.now().strftime(T_FORMAT)
    end = datetime.datetime.now().strftime(T_FORMAT)
    em = EmailNotifier("ddx30", "Ubuntu", "exclusive",
                       start, end, 1, "testing")
    em.send_ddx_failure_email("..")
