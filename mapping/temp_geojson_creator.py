import pandas as pd
import geojson
import csv

#Ideas - thing out j_data (joined data frame) to make the data lighter
#before converting to geojson

###########
#variables#
###########

temp_file = "C:/Sandbox/geojson/college_valley_1_temperature.log"
gps_file = "C:/Sandbox/geojson/college_valley_1.log"
out_file = "C:/Sandbox/geojson/test3.geojson"

############
#functions#
###########

def read_log(file):
    the_list = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            the_list.append(row)
    return(the_list)

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]
   
def df_to_geojson(df,out_file):
    features = []
    insert_features = lambda X: features.append(
            geojson.Feature(geometry=geojson.Point((X["lon"],
                                                    X["lat"])),
                            properties=dict(date=X["date"],
                                            time=X["time"],
                                            temp=X["temp"])))
    df.apply(insert_features, axis=1)
    with open(out_file, 'w', encoding='utf8') as fp:
        geojson.dump(geojson.FeatureCollection(features), fp, sort_keys=True, ensure_ascii=False)

##############
#running code#
##############

#temperature data
temp_list = read_log(temp_file)
#filter
temp_list = [k for k in temp_list if "New session started..." not in k]
#remove empty lines
temp_list = list(filter(None, temp_list))
temp_df = pd.DataFrame(temp_list, columns = ["date", "time", "id", "temp"])
#calculate a mean temperature for repeat measures on a given time stamp
temp_df[['temp']] = temp_df[['temp']].apply(pd.to_numeric)
temp_df = temp_df.groupby(['date','time'], as_index=False).mean()

#GPS data
gps_list = read_log(gps_file)
#filter
gps_list = [k for k in gps_list if "New session started..." not in k and
                                   "No data feed from driver" not in k and
                                   "No driver found" not in k and
                                   "Now using GPS date and time" not in k]
gps_df = pd.DataFrame(gps_list, columns = ["date", "time", "lat", "lon", 
                                           "alt", "num_sats", "hdop", "qi", 
                                           "code"])
#filter out fixes
gps_df = gps_df[gps_df['code'] == "FIX"]
#select only wanted columns
gps_df = gps_df[["date","time","lat","lon"]]


#join data frames
j_data = pd.merge(temp_df, gps_df, on=['date','time'], how='inner')
#ensure numeric columns are numeric!
j_data[['lat','lon']] = j_data[['lat','lon']].apply(pd.to_numeric)
#drop duplicate times
j_data = j_data.drop_duplicates("time")


df_to_geojson(j_data,out_file)





