#!/usr/bin/python3
# -*- coding: utf8 -*-
#Copyright (C) 2015 Guillaume DUPUY <glorf@glorf.fr>
#This file is part of Watch Poe.

#Watch PoE is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Watch PoE is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>
import os
from datetime import datetime
from log import logger
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
        logger.info("Sent PoE Message Warning (at {0}) : {1}".format(datetime.now().strftime("%H:%M"), msg.rstrip("\n")))
