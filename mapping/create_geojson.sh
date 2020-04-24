#!/bin/bash

python3 gps_geojson_creator.py $1
python3 temp_geojson_creator.py $1
#python3 hydrophone_processing.py $1
#python3 foi_geojson_creator.py $1
