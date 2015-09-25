#!/usr/bin/python3
# -*- coding: utf8 -*-
#Copyright (C) 2015 Guillaume DUPUY <glorf@glorf.fr>
#This file is part of Poe Watcher.

#PoE Watcher is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#PoE Watcher is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>
from . import config as c
from . import utils
import logging
import os
logger = logging.getLogger(__name__)
class CsvManager():
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.read_file()
    def read_file(self):
        """ Read a .csv and put it in a dict """
        if os.path.isfile(self.filename):
            with open(self.filename, "r", encoding="utf-8") as file:
                file.readline() #Don't use first line [headers]
                for line in file:
                    self.data.append(utils.dict_from_csv(line))
        else:
            logger.warning("Tried to open {0} but couldn't :|".format(self.filename))
    def write_to_tackle_csv(self, output_path):
        """ Use the self.data to put all information into a csv with the right format for tacke70's spreadsheet [ see http://exiletools.com/tackle70/ ] """
        if os.path.isfile(output_path):
            logger.warning("The output {0} already exists ; i deleted it to write the new one".format(output_path))
        with open(output_path, "w", encoding="utf-8")as file:
            for d in self.data:
                output = utils.dict_to_tackle_csv(d)
                file.write(output)
                file.write("\n")
