#!/usr/bin/python3
# -*- coding: utf8 -*-
import os
from datetime import datetime
class Notifier():
    def __init__(self, channels, title, icon_path, windows):
        self.channels = channels
        self.title = title
        self.icon_path = icon_path
        self.windows = windows
    def parse_message(self, msg):
        if any(ext in msg[0] for ext in self.channels):
            self.send_notification(msg)
    def send_notification(self, msg):
        cmd ='-i {0} "{1}" "{2}"'.format(self.icon_path, self.title, msg)
        if self.windows:
            subprocess.call('notify-send.exe ' + cmd)
        else:
            os.system('notify-send ' + cmd)
        #rstrip for prettyness (else we have an unnecessary newline)
        print("Sent PoE Message Warning (at {0}) : {1}".format(datetime.now().strftime("%H:%M"), msg.rstrip("\n")))
