#!/usr/bin/python3
# -*- coding: utf8 -*-

#Global
#Separator for options in commands
separator = ","
#Your characters names
usernames = ["Glorf", "Faaee"]
log_path = "/opt/pathofexile/drive_c/Program Files/Grinding Gear Games/Path of Exile/logs/"
#Number of boss killed by maps
default_boss = 1
#MapRecorder config
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
