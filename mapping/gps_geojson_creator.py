import csv
import json
import pandas as pd
import os
import json
import sys

###########
#variables#
###########

log_path = sys.argv[1] 
gps_log_name = "adv_gps.log"

out_path = "."
out_file = "gps_track.geojson"

if not os.path.isdir(out_path):
	os.mkdir(out_path)

###########
#functions#
###########

def read_log(file):
    the_list = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            the_list.append(row)
    return(the_list)

def format_gps_log(file):
    log_list = read_log(file)
    log_list = [k for k in log_list if "New session started..." not in k and
                                   "No data feed from driver" not in k and
                                   "No driver found" not in k and
                                   "Now using GPS date and time" not in k]
    log_df = pd.DataFrame(log_list, columns = ["date", "time", "lat", "lon", 
                                           "alt", "num_sats", "hdop", "qi", 
                                           "code"])
    #filter out fixes
    log_df = log_df[log_df['code'] == "FIX"]
    #select only wanted columns
    log_df = log_df[["date","time","lat","lon"]]
    log_df[['lat','lon']] = log_df[['lat','lon']].apply(pd.to_numeric)
    return(log_df)
    
#function to create geojson linestring (manually)
#input should be a data frame with 'lat' and 'lon' columns
def df_to_geojson(df, out_file):
    coords = []
    #combine coords into a list
    for index, row in df.iterrows():
        points = [row["lon"],row["lat"]]
        coords.append(points)
    #construct geojson
    out = {"type":'FeatureCollection',
           'name':'testline',
           "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" }},
           'features':[
               {"type": "Feature", "properties": { "fid": 1},
                        "geometry": { "type": "LineString", "coordinates" : coords}}
                        ]
    }
    with open(out_file, 'w') as file:
     file.write(json.dumps(out, indent = 1))

##############
#running code#
##############

a = format_gps_log(log_path + "/" + gps_log_name)
df_to_geojson(a, out_path + "/" + out_file)
