import pandas as pd
import geojson
import csv

#Ideas - thing out j_data (joined data frame) to make the data lighter
#before converting to geojson

###########
#variables#
###########

log_path = "C:/Sandbox/geojson"
temp_log_name = "college_valley_1_temperature.log"
gps_log_name = "college_valley_1.log"

out_path = "C:/Sandbox/geojson"
out_file = "temp_test1.geojson"

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

#def remove_values_from_list(the_list, val):
#   return [value for value in the_list if value != val]

def format_temp_log(file):
    log_list = read_log(file)
    log_list = [k for k in log_list if "New session started..." not in k]
    #remove empty lines
    log_list = list(filter(None, log_list))
    log_df = pd.DataFrame(log_list, columns = ["date", "time", "id", "temp"])
    #calculate a mean temperature for repeat measures on a given time stamp
    log_df[['temp']] = log_df[['temp']].apply(pd.to_numeric)
    log_df = log_df.groupby(['date','time'], as_index=False).mean()
    return(log_df)
    
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
    return(log_df)
    
def join_temp_gps(temp_df, gps_df):
    #join data frames
    j_data = pd.merge(temp_df, gps_df, on=['date','time'], how='inner')
    #ensure numeric columns are numeric!
    j_data[['lat','lon']] = j_data[['lat','lon']].apply(pd.to_numeric)
    #drop duplicate times
    j_data = j_data.drop_duplicates("time")
    return(j_data)

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

temp_df = format_temp_log(log_path + "/" + temp_log_name)

gps_df = format_gps_log(log_path + "/" + gps_log_name)

j_data = join_temp_gps(temp_df, gps_df)

df_to_geojson(j_data, out_path + "/" + out_file)