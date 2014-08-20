# -*- coding: utf-8 -*-
__author__ = 'wangting'


from commands.docker_base import DockerBase
import threading
import smtplib
from pprint import pprint


class Monitor(DockerBase):

    def monitor_containers(self, container_ids, email_list):
        stopped_container_id = []
        for id in container_ids:
            status = self.d.get_container_details(id)
            if not status['State']['Running']:
                stopped_container_id.append(id)
        if len(stopped_container_id) > 0:
            ids = ",".join(stopped_container_id)
            text = "Container %s are down!" % ids
            self.send_email(text, email_list)
        threading.Timer(
            self.config.get('base', 'WATCH_INTERVAL'), self.monitor_containers, [container_ids, email_list]
        ).start()

    def monitor_container(self, container_id, email_list):
        status = self.d.get_container_details(container_id)
        if not status['State']['Running']:
            text = "Container %s is down!" % container_id
            self.send_email(text, email_list)
        threading.Timer(
            self.config.get('base', 'WATCH_INTERVAL'), self.monitor_container, [container_id, email_list]
        ).start()

    def monitor(self, group_name):
        pass

    def send_email(self, text, to):
        user = self.config.get('base', 'SMTP_USER')
        password = self.config.get('base', 'SMTP_PASSWORD')
        f = self.config.get('base', 'SMTP_FROM')
        subject = 'ALERT! Docker Monitoring'

        message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (f, ", ".join(to), subject, text)
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


