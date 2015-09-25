#!/bin/bash
#Run it on a cronjob or something
DATA_PATH="/home/glorf/poewatcher/server/data/"
OUTPUT="/home/glorf/poe/map_data.csv"
cd $DATA_PATH
cat *.csv > $OUTPUT
