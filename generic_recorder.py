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
from log import logger
import time
class GenericRecorder():
    def __init__(self, actions, separator, output_path, headers):
        
        self.output_path = output_path
        self.separator = separator
        self.headers = headers
        self.actions = []
        for pr in actions:
            self.actions.append((pr[1], getattr(self, pr[2])))
        if not os.path.isfile(output_path):
            open(output_path, "w+", encoding='utf8')
        with open(output_path, "r+", encoding='utf8') as file:
            if os.path.getsize(output_path) == 0:
                file.write(','.join(headers))
                file.write("\n")
                logger.info("Created output csv file for GenericRecorder")
    def parse_message(self, msg, char_name):
        for abbr,func in self.actions:
            if abbr in msg:
                func(msg.replace(abbr,""), char_name)
    def add_loot(self, msg, char_name):
        info = [char_name, str(int(time.time()))]
        info += msg.split(self.separator)
        while len(info) < len(self.headers):
            info.append("")
        csv = ",".join(info)
        with open(self.output_path, "a", encoding='utf8') as file:
            file.write(csv)
            file.write("\n")
        logger.info("GenericRecorder wrote : {0}".format(csv))
