import os
import subprocess
from subprocess import DEVNULL

############
#functions##
############


#takes a fix containing a time, formats and outputs an array "hh:mm:ss"
def process_time(fix):
    #number of numbers
    n = 2
    temp = str(fix["time"])
    #split every two numbers to give hours/mins/secs
    temp = [temp[i:i+n] for i in range(0, len(temp), n)]
    #add ':'' delims
    fix["time"] = temp[0] + ":" + temp[1] + ":" + temp[2]


#check direction of lat/lon values and make negative if required
def process_lat_lon(fix):
    #move decimal into correct place to display decimal degrees
    fix["lon"] = fix["lon"]/100
    fix["lat"] = fix["lat"]/100
    #correct for positions make negative for W and S coords
    if fix["lon_dir"] == "W":
        fix["lon"] = -fix["lon"]
    if fix["lat_dir"] == "S":
        fix["lat"] = -fix["lat"]
    #stringify
    fix["lon"] = str(fix["lon"])
    fix["lat"] = str(fix["lat"])


#takes '$GPGGA' data from NMEA logs and returns processed information
def gpgga_read(line):
    #split by comma
    data = line.split(",")
    #create dict to store pieces of info from GPGGA data
    fix = {"time":int(float(data[1])),
    "lat":float(data[2]),
    "lat_dir":data[3],
    "lon":float(data[4]),
    "lon_dir":data[5],
    "qi":data[6],
    "num_sats":data[7],
    "hdop":data[8],
    "alt":data[9]}
    #apply functions to format time and coords
    process_time(fix)
    process_lat_lon(fix)
    return(fix)


#takes a line from GPS device and outputs arrays of processed data
def gps_read(line):
    gpgga_data = []
    #remove whitespace
    line = line.strip()
    #store data if its the correct format
    if line.startswith("$GPGGA"):
        gpgga_data.append(gpgga_read(line))
    return(gpgga_data)


###############
#running code##
###############

#ensure that GPS is in NMEA mode

#run once
#subprocess.call(["sudo", "apt-get", "install", "gpsd-clients"],
#    stderr=DEVNULL, stdout=DEVNULL)
subprocess.call(["sudo", "stty", "-F", "/dev/ttyUSB0", "4800"],
    stderr=DEVNULL, stdout=DEVNULL)
subprocess.call(["sudo", "gpsctl", "-n", "-D", "4", "/dev/ttyUSB0"],
    stderr=DEVNULL, stdout=DEVNULL)


#set location of GPS device output 
path = '/dev'
os.chdir(path)
dat = open('ttyUSB0')

#infinite loop
while True:
    datc = dat.readline()
    #format the data and read out to terminal
    for datc_f in gps_read(datc):
        out = datc_f["time"] + "," + datc_f["lat"] + \
        "," + datc_f["lon"] + "," + datc_f["alt"] + \
        "," + datc_f["num_sats"] + "," + datc_f["hdop"] + \
        "," + datc_f["qi"] 
        print(out)
datc.close()