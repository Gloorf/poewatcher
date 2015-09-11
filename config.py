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
import configparser
import json
from ast import literal_eval as make_tuple
import click
import os
APP_NAME="Watch PoE"
class Config(configparser.ConfigParser):
    def __init__(self):
        super().__init__(interpolation=None)
    def get_actions(self, section):
        raw = self.get(section, "actions").split("\n")
        out = []
        for i in raw:
            out.append(make_tuple(i))
        return out
    def get_list(self, section, name):
        return json.loads(self.get(section, name))

config = Config()    
cwd = os.path.join(click.get_app_dir(APP_NAME), "config.ini")
if os.path.isfile(cwd):
    config.read(cwd)
else:
    config.read("config.ini")
