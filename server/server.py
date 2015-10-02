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

import socketserver
import json
import logging
import os
import sys
from collections import OrderedDict
sys.path.insert(0, '..')
from poewatcher import Map
DATA_PATH = "data/"
HOST = "localhost"
PORT = 8095
logging.basicConfig(filename='watch_poe.log', format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG)
#Kept for compatibility sake
def to_csv(data):
    out = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}".format(data["timestamp"], data["character"], data["level"], data["psize"], data["iiq"], data["boss"], data["ambush"], data["beyond"], data["domination"],data["magic"], data["zana"])
    for i in range(68,83):
        out += "," + str(data["loot"].count(i))
    return out    
def save_data(data, ip):
    csv = to_csv(data)
    output_path = DATA_PATH + "legacy/" + ip + ".csv"
    if not os.path.isfile(output_path):
        logging.info('Created file %s', output_path)
        open(output_path, "w+")
    
    with open(output_path, "a") as file_out:
        file_out.write(csv)
        file_out.write("\n")
def save_new_data(data, ip):
    csv = data.to_csv()
    output_path = DATA_PATH + "current/" + ip + ".csv"
    if not os.path.isfile(output_path):
        logging.info('Created file %s', output_path)
        open(output_path, "w+")
    
    with open(output_path, "a") as file_out:
        file_out.write(csv)
        file_out.write("\n")    
    
class PoeTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        client_ip = self.client_address[0]
        try:
            b = b''
            b = self.request.recv(8192)
            raw_json = b.decode('utf-8')
            data = json.loads(raw_json)
            
            if "is_obj" in data:
                m1=Map.from_json(raw_json)
                save_new_data(m1, client_ip)
                logging.info('{0} - Current version - OK'.format(client_ip))
                self.request.sendall(b'OK')
            else:
                save_data(data, client_ip)
                logging.info('{0} - Legacy version - OK'.format(client_ip))
                legacy = b'OK - You are using an old version of poewatcher. Please go to https://github.com/Gloorf/poewatcher/releases and download the new version !'
                self.request.sendall(legacy)
                # error = b'FAIL'
                # logging.warning('%s - FAIL', client_ip)
                # self.request.sendall(error)
        except Exception as e:
            error = "FAIL - {0}".format(e)
            logging.warning('{0} - FAIL - {1}'.format(client_ip,e))
            self.request.sendall(error.encode('utf-8'))

    
#see https://www.pathofexile.com/forum/view-thread/537709#p4832625

# Create the server,
server = socketserver.TCPServer((HOST, PORT), PoeTCPHandler)

# Activate the server; this will keep running until you
# interrupt the program with Ctrl-C
server.serve_forever()
