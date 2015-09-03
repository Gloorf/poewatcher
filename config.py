#!/usr/bin/python3
# -*- coding: utf8 -*-

#Copyright (C) 2015 Guillaume DUPUY <glorf@glorf.fr>
#This file is part of Watch Poe.

#Watch PoE is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Watch PoE is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>


#Global
#Separator for options in commands
separator = ","
#Your characters names
usernames = ["Glorf", "Faaee"]
log_path = "/opt/pathofexile/drive_c/Program Files/Grinding Gear Games/Path of Exile/logs/"
#Number of boss killed by maps
default_boss = 1
#MapRecorder config
#Values are "" (the character name who wrote in local will be used), "anonymous" if you don't want to log it, or "Glorf"(any fixed username) if you want it to stay the same
logged_username = ""
map_output_path = "map_data.csv"
#(action, shortcut, function_name) : absolutely DON'T change function name, action is here only for clarity
map_actions = [("start", "ms:", "add_map"), 
            ("loot", "ml:", "add_loot"),
            ("note", "mn:", "add_note"),
            ("end", "me:", "end_map") ]
#GenericRecorder config
generic_headers = ["numbers of unique", "numbers of rare", "numbers of 6sockets"]
generic_actions = [ ("loot", "gl:", "add_loot")]
generic_output_path = "generic_data.csv"
#Notifier config        
#Path needs to be absolute, or notify-send won't work    
notifier_icon_path = "/home/glorf/code/watch_poe/logo.png"
notifier_channels = ["@","%","&","#"]
notifier_title = "PoE message"
