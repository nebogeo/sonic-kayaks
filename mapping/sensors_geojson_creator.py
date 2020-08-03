import pandas as pd
import geojson
import csv
import os
import sys

#Ideas - thin out j_data (joined data frame) to make the data lighter
#before converting to geojson

sensor_cols = ["date", "time", "temp",
                "pm_running", "temp_error", "pm_error",
                "pm_id", "pm_frame_len",
                "pm_std_1_0", "pm_std_2_5", "pm_std_10_0",
                "pm_env_1_0", "pm_env_2_5", "pm_env_10_0",
                "pm_np_0_1", "pm_np_0_5", "pm_np_1_0", "pm_np_2_5", "pm_np_5_0", "pm_np_10_0",
                "pm_res", "pm_checksum",
                "turbid_raw",
                "turbid_filt_1", "turbid_filt_2", "turbid_filt_3",
                "turbid_filt_4", "turbid_filt_5", "turbid_filt_6",
                "turbid_filt_7","blank"]

###########
#variables#
###########

log_path = sys.argv[1]
sensor_col = sys.argv[2]
sensors_log_name = "sensors.csv"
gps_log_name = "adv_gps.log"

out_path = "."
out_file = sensor_col+".geojson"

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

def format_sensors_log(file,col):
    log_list = read_log(file)
    log_list = [k for k in log_list if "New session started..." not in k]
    #remove empty lines
    log_list = list(filter(None, log_list))
    log_df = pd.DataFrame(log_list, columns = sensor_cols)
    #calculate a mean for repeat measures on a given time stamp
    log_df[[col]] = log_df[[col]].apply(pd.to_numeric)
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
    
def join_sensors_gps(sensors_df, gps_df):
    #join data frames
    j_data = pd.merge(sensors_df, gps_df, on=['date','time'], how='inner')
    #ensure numeric columns are numeric!
    j_data[['lat','lon']] = j_data[['lat','lon']].apply(pd.to_numeric)
    #drop duplicate times
    j_data = j_data.drop_duplicates("time")
    return(j_data)

def df_to_geojson(df,out_file, sensor_col):
    features = []
    insert_features = lambda X: features.append(
            geojson.Feature(geometry=geojson.Point((X["lon"],
                                                    X["lat"])),
                            properties=dict(date=X["date"],
                                            time=X["time"],
                                            data=X[sensor_col])))
    df.apply(insert_features, axis=1)
    with open(out_file, 'w', encoding='utf8') as fp:
        geojson.dump(geojson.FeatureCollection(features), fp, sort_keys=True, ensure_ascii=False)

##############
#running code#
##############


with open("temp.csv","w") as csvoutfile:
    w = csv.writer(csvoutfile)
    with open(log_path + "/" + sensors_log_name, newline='') as csvfile:
        r = csv.reader(csvfile)
        for n,row in enumerate(r):
            passed=True
            for i in row:
                if i=="N/A": passed=False
            if passed:
                w.writerow(row)


sensors_df = format_sensors_log("temp.csv", sensor_col)
gps_df = format_gps_log(log_path + "/" + gps_log_name)
j_data = join_sensors_gps(sensors_df, gps_df)
df_to_geojson(j_data, out_path + "/" + out_file, sensor_col)
print("written to: "+out_path + "/" + out_file)
