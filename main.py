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
import logging.config
logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

from poewatcher import MapRecorder, Notifier, GenericRecorder, PoeHandler
from poewatcher import config as c
from poewatcher import windows
from poewatcher import utils
import time
##Init stuff
map_recorder = MapRecorder(c.get_actions("map_recorder"), c.get("global","separator"), c.get("map_recorder","output_path"))
notifier = Notifier(c.get_list("notifier","channels"), c.get("notifier","title"), c.get("notifier","icon_path"), windows)
generic_recorder = GenericRecorder(c.get_actions("generic_recorder"), c.get("global","separator"), c.get("generic_recorder","output_path"), c.get_list("generic_recorder","headers"))
poe_handler = PoeHandler(c.get_list("global","usernames"), c.get_actions("handler"), c.get("global","log_path"))
logger.info("started watch_poe")
##Main loop
try:
    while True:
        time.sleep(1)
        ##Where all the dirty work is done
        poe_handler.read_new_lines()
        for message in poe_handler.messages:
            if not utils.poe_active() and poe_handler.notifier:
                notifier.parse_message(message)
            stripped, name = poe_handler.strip_username(message)
            name = c.get("map_recorder","logged_username") if c.get("map_recorder","logged_username") else name
            if stripped:
                old_state = map_recorder.running()
                map_recorder.parse_message(stripped, name)
                generic_recorder.parse_message(stripped, name)
                state = map_recorder.running()
                #Change of stat (either map started/map ended)
                if c.getboolean("handler","offline_while_maps") and state != old_state:
                    if state:
                        poe_handler.poetrade_off()
                    else:
                        poe_handler.poetrade_on()
        
        poe_handler.messages.clear()
            

            
except KeyboardInterrupt:
    logger.info("Stopping watch_poe")


