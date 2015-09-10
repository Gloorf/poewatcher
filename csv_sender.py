#!/usr/bin/python3
# -*- coding: utf8 -*-
from config import config as c
import util
"""
Use only once, to send a whole CSV file. Ignores first line (assumed to be headers)
"""
with open(c.get("map_recorder", "output_path"), "r") as file:
    file.readline() #Go past first line[headers]
    for line in file:
        k = util.contact_server(util.dict_from_csv(line))
