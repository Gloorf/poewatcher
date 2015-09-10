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
import logging

# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console & file handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
f = logging.FileHandler("watch_poe.log")
f.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# add formatter to ch & f
ch.setFormatter(formatter)
f.setFormatter(formatter)


# add both handler
logger.addHandler(ch)
logger.addHandler(f)


