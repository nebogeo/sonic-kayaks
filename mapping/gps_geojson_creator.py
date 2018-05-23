import csv
import pandas as pd
import geojson


###########
#variables#
###########

log_path = "C:/foam/sonic_kayaks/sandbox/foi_gps_test"
gps_log_name = "adv_gps.log"

out_path = "C:/foam/sonic_kayaks/sandbox/foi_gps_test"
out_file = "gps_track.geojson"

if not os.path.isdir(out_path):
	os.mkdir(out_path)


#############
##functions##
#############

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
    
def df_to_geojson(df,out_file):
    features = []
    insert_features = lambda X: features.append(
            geojson.Feature(geometry=geojson.LineString((X["lon"],
                                                    X["lat"])),
                            properties=dict(date=X["date"],
                                            time=X["time"])))
    df.apply(insert_features, axis=1)
    with open(out_file, 'w', encoding='utf8') as fp:
        geojson.dump(geojson.FeatureCollection(features), fp, sort_keys=True, ensure_ascii=False)
        
        
################
##running code##
################

a = format_gps_log(log_path + "/" + gps_log_name)
b = df_to_geojson(a, out_path + "/" + out_file)

