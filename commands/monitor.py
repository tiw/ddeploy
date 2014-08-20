# -*- coding: utf-8 -*-
__author__ = 'wangting'


from commands.docker_base import DockerBase
import threading
import smtplib
from pprint import pprint


class Monitor(DockerBase):
    def monitor_container(self, container_id, email_list):
        status = self.d.get_container_details(container_id)
        if status['State']['Running']:
            threading.Timer(10, self.monitor_container, [container_id]).start()
        else:
            text = "Container %s is down!" % container_id
            self.send_email(text, email_list)

    def monitor(self, group_name):
        pass

    def send_email(self, text, to):
        user = self.config.get('base', 'SMTP_USER')
        password = self.config.get('base', 'SMTP_PASSWORD')
        f = self.config.get('base', 'SMTP_FROM')
        subject = 'ALERT! Docker Monitoring'

        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (f, ", ".join(to), subject, text)
        try:
            server = smtplib.SMTP(self.config.get('base', 'SMTP_SERVER'))
            server.ehlo()
            server.starttls()
            server.login(user, password)
            server.sendmail(f, to, message)
            server.close()
            print "successfully"
        except Exception as e:
            pprint(e)
            print "failed"


