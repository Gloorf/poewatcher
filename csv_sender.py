#!/usr/bin/python3
# -*- coding: utf8 -*-
from poewatcher import config as c
from poewatcher import utils
"""
Use only once, to send a whole CSV file. Ignores first line (assumed to be headers)
"""
with open(c.get("map_recorder", "output_path"), "r", encoding='utf-8') as file:
    file.readline() #Go past first line[headers]
    for line in file:
        k = utils.contact_server(utils.dict_from_csv(line))
        print("Received : {0}".format(k))
