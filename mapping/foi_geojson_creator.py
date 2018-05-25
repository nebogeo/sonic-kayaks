import csv
import pandas as pd
import geojson
import os

#assumes GPS stays fixed once it gets a fix - for now...

###########
#variables#
###########

#define lag time (startup of GPS before recording)
#lag mainly caused by executing NMEA mode functions
startup_lag = 10 #in seconds
driver_retry_time = 5 # from gps driver

#log_path = "/home/pi/audio/audiotest/logs"
log_path = "C:/foam/sonic_kayaks/sandbox/foi_gps_test"
foi_name = "foi.txt" #frequency of interest data
gps_log_name = "adv_gps_sub.log"

out_path = "C:/foam/sonic_kayaks/sandbox/foi_gps_test"
out_file = "hydro_foi_test1.geojson"

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
    
#work out how much delay before the GPS starts collecting data (NOFIX or FIX) 
def calculate_lag(file, startup_lag, driver_retry_time):
    log_list = read_log(file)
    nd_count =  [k for k in log_list if 'No driver found' in k]
    lag_time = (len(nd_count)*driver_retry_time)
    
    ##Work out length of NOFIX readings
    log_list = [k for k in log_list if "New session started..." not in k and
                                   "No data feed from driver" not in k and
                                   "No driver found" not in k and
                                   "Now using GPS date and time" not in k]
    log_df = pd.DataFrame(log_list, columns = ["date", "time", "lat", "lon", 
                                           "alt", "num_sats", "hdop", "qi", 
                                           "code"])
                                           
    nofix_count = len(log_df[log_df['code'] == "NOFIX"])
    lag_time = startup_lag + lag_time + nofix_count
    return(int(lag_time))
    
def format_foi(file):
    #read in hydrophone foi info as dataframe
    foi_df = pd.read_table(file, sep = ",")
    #trim down - now the start is lined up with the first fix.
    foi_df = foi_df.drop(foi_df.index[0:total_lag-1])
    return(foi_df)
    
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
    
def join_foi_gps(foi_df, gps_df):
    #match length of data frames, considering which one is longer
    if len(gps_df)-len(foi_df) <0:
        foi_df = foi_df[:len(gps_df)-len(foi_df)]
    elif len(gps_df)-len(foi_df) >0:
        gps_df = gps_df[:-(len(gps_df)-len(foi_df))]
    #join together
    foi_df=foi_df.reset_index()
    gps_df=gps_df.reset_index()
    j_data = pd.concat([gps_df, foi_df], axis = 1)
    j_data[['lat','lon', 'big_boat', 'medium_boat']] = \
    j_data[['lat','lon', 'big_boat', 'medium_boat']].apply(pd.to_numeric)
    return(j_data)

#modify function to incorporate more frequencies of interest
def df_to_geojson(df,out_file):
    features = []
    insert_features = lambda X: features.append(
            geojson.Feature(geometry=geojson.Point((X["lon"],
                                                    X["lat"])),
                            properties=dict(date=X["date"],
                                            time=X["time"],
                                            big_boat=X["big_boat"],
                                            medium_boat=X["medium_boat"])))
    df.apply(insert_features, axis=1)
    with open(out_file, 'w', encoding='utf8') as fp:
        geojson.dump(geojson.FeatureCollection(features), fp, sort_keys=True, ensure_ascii=False)

##############
#running code#
##############

#total number of seconds to be removed from start of log
total_lag = calculate_lag(log_path + "/" + gps_log_name, startup_lag, driver_retry_time)
#process foi data
foi_df = format_foi(log_path + "/" + foi_name)
#process the GPS data, selecting fixes
gps_df = format_gps_log(log_path + "/" + gps_log_name)
#join together
j_data = join_foi_gps(foi_df, gps_df)
#export as geojson
df_to_geojson(j_data, out_path + "/" + out_file)