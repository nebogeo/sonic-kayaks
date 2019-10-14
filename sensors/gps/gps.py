#Issues:
#readline pulling broken lines from proper $GPGGA reads then erroring on dictionary creation...
#either need to modify readlines or add in more checks for quality of string...

import glob
import os
import subprocess
from subprocess import DEVNULL
import time
from datetime import datetime
import serial

#the different states in the processing workflow
start_state = 0
no_device_state = 1
waiting_state = 2
date_found_state = 3
position_found_state = 4
valid_date_state = 5
nofix_state = 6
valid_position_state = 7

###########
#variables#
###########

#device_file = "/dev/ttyS0"
device_file = "/dev/ttyUSB0"
baud_rate = 4800
log_path = "/home/pi/stick/sonickayak/logs/adv_gps.log"
pipe_path = "/dev"
pipe_name = "/tmp/swamp_gps"

#when there is no driver detected, no. seconds to wait before retrying
driver_retry_time = 5
#position of the date in $GPRMC/$GNRMC codes
gprmc_date_position = 9
#position of the time in $GPRMC/$GNRMC codes
gprmc_gpgga_time_position = 1
#position of latitude in $GPGGA/$GNGGA codes
gpgga_lat_position = 2

#record output messages to a log file
def log(text):
    adv_log = open(log_path, "a")
    adv_log.write(text + "\n")
    adv_log.close()

class gps_reader:

    pipe_name = "/tmp/swamp_gps"
    the_pipe = "" # empty variable for the fifo pipe to inhabit
    pipe_flag = False # only need to open the pipe once...
    
    current_drivers = "" # list of current drivers matching driver path
    drivers = "" # list of available drivers found at driver path (gets updated, removing elements when trying to find a driver)
    gps_feed = False
    newline = "" # each line as it comes in
    the_date = "N/A" # global date variable
    the_time = "N/A" # global time variable
    date_flag = False # has date has been grabbed from GPS
    time_flag = False # has time has been grabbed from GPS

    state = start_state

    def __init__(self,driver_path):
            self.driver_path = driver_path
            

    ###########
    #functions#
    ###########
            
    #open the fifo pipe
    def pipe_open(self):
        #set location of GPS device output and open pipe
        if not os.path.exists(self.pipe_name): os.mkfifo(self.pipe_name)
        self.the_pipe = os.open(self.pipe_name, os.O_WRONLY)
        self.pipe_flag = True
        
    #write valid coords to the fifo pipe    
    def pipe_write(self, dict_in):
        os.write(self.the_pipe,
        bytes("%s %s\n"%(dict_in["lat"],dict_in["lon"]),'UTF-8'))
    
    #write nofix coords into fifo pipe
    def pipe_write_nofix(self):
        os.write(self.the_pipe,
        bytes("%s %s\n"%(999,999),'UTF-8'))
    
    #return drivers matching driver locations
    def detect_drivers(self, location):
        driver_list = glob.glob(location + "*")
        return(driver_list)
    
    #check for presence of the GPS driver input driver path
    def check_driver(self,location):
        try:
                    #self.gps_feed = open(location)
                    self.gps_feed = serial.Serial(location,baud_rate)
                    return True
        except FileNotFoundError:
                    return False
        except:
                    return False
        
    #check for feed of data from the GPS driver
    def get_line(self):
        try:
            raw_feed = self.gps_feed.readline()
            #print(raw_feed)
            return raw_feed.decode("ascii")
        except:
            return False

    #check if there is a date present in $GPRMC/$GNRMC data
    def date_presence(self,line):
        if line[gprmc_date_position]:
            return True
        else:
            return False
    
    #pull date and time from GPS feed
    def update_time_date(self,line):
        raw = line.split(",")
        raw_date = raw[gprmc_date_position]
        raw_time = raw[gprmc_gpgga_time_position]
        #rearrange numbers, adding a 20 in
        corr_date = "20" + raw_date[4:6] + raw_date[2:4] + raw_date[0:2]
        #number of numbers for each time component
        n = 2   
        #split every two numbers to give hours/mins/secs
        raw_time = [raw_time[i:i+n] for i in range(0, len(raw_time), n)]
        #add ':'' delims to make human readable
        # quick check here...
        if len(raw_time)<3: return
        corr_time = raw_time[0] + ":" + raw_time[1] + ":" + raw_time[2]
        subprocess.call(['sudo', 'date', '+%Y%m%d', '-s', corr_date],
        stderr=DEVNULL, stdout=DEVNULL)
        subprocess.call(['sudo', 'date', '+%T', '-s', corr_time], 
        stderr=DEVNULL, stdout=DEVNULL)
        
        self.the_date = corr_date
        self.the_time = corr_time
        
        self.date_flag = True
        self.time_flag = True
    
    #check if there are coordinates present in $GPGGA/$GNGGA data    
    def position_presence(self,line):
        line = line.split(",")
        if line[gpgga_lat_position]:
            return True
        else:
            return False

    #formats the date in a dictionary into a human readable format
    def format_date(self):
        #rearrange numbers, making them human readable
        self.the_date = self.the_date[0:4] + ":" + self.the_date[4:6] + ":" + \
        self.the_date[6:8]

    #formats the time for a time dictionary variable        
    def format_time(self,in_dict):
        #number of numbers
        n = 2
        temp = str(in_dict["time"])
        
        #hours in the morning miss a preceeding 0, e.g. 9 instead of 09
        if len(temp) == 5:
            temp = "0" + temp
        
        #split every two numbers to give hours/mins/secs
        temp = [temp[i:i+n] for i in range(0, len(temp), n)]
        #add ':'' delims
        in_dict["time"] = temp[0] + ":" + temp[1] + ":" + temp[2]
  
    #when no position is present, format the data for the log with NOFIX
    def format_nofix(self, line): 
        data = line.split(",")
        
        #create a dict to store data   
        no_fix = {"date":self.the_date,
        "time":int(float(data[gprmc_gpgga_time_position])),
        "lat":'0',
        "lat_dir":'0',
        "lon":'0',
        "lon_dir":'0',            
        "qi":'0',
        "num_sats":'0',
        "hdop":'0',
        "alt":'0',
        "code":'NOFIX'}
        
        self.format_time(no_fix)
        return(no_fix) 

    #format the lat and lon for each variable in a dictionary    
    def format_lat_lon(self,fix):
        
        #format position information (from d/m to decimals)
        fix["lat"] = float(fix["lat"][0:2]) + \
        float(fix["lat"][2:])/60

        fix["lon"] = float(fix["lon"][0:3]) + \
        float(fix["lon"][3:])/60

        #correct for positions, make negative for W and S
        if fix["lon_dir"] == "W":
            fix["lon"] = -fix["lon"]
        if fix["lat_dir"] == "S":
            fix["lat"] = -fix["lat"]
        #stringify
        fix["lon"] = str(fix["lon"])
        fix["lat"] = str(fix["lat"])
    
    #knowing that latitude is present, format all GPS data in a dictionary
    def format_position(self,line):
        data = line.split(",");
        #create a dict to store data
        fix = {"date":self.the_date,
            "time":int(float(data[1])),
            "lat":data[2],
            "lat_dir":data[3],
            "lon":data[4],
            "lon_dir":data[5],
            "qi":data[6],
            "num_sats":data[7],
            "hdop":data[8],
            "alt":data[9],
            "code":"FIX"} 
        
        self.format_time(fix)
        self.format_lat_lon(fix)
        return(fix)
  
    #formats a dictionary of position information and writes to the log    
    def log_position(self,pos_data):
        out = pos_data["date"] + "," + pos_data["time"] + "," + \
        pos_data["lat"] + "," + pos_data["lon"] + "," + pos_data["alt"] + \
        "," + pos_data["num_sats"] + "," + pos_data["hdop"] + "," + \
        pos_data["qi"] + "," + pos_data["code"]
        log(out)
               
    #main state function
    def update_state(self):
        #print(self.state)
    
        if self.state == start_state:
                        
            #find all drivers
            self.drivers = self.detect_drivers(self.driver_path)
            
            #check if there are drivers available
            if self.drivers:
                
                #make a local copy of the class variable
                self.current_drivers = list(self.drivers)
                
                #drop first driver from the class variable
                del self.drivers[0]
                
                #try the first driver in the list
                if self.check_driver(self.current_drivers[0]):
                    self.state = waiting_state
                else:
                    self.state = no_device_state
            
        elif self.state == no_device_state:
            log("No driver found")
            time.sleep(driver_retry_time) 
            self.state = start_state

        elif self.state == waiting_state:
            self.newline = self.get_line()

            #is the data an actual line of information?
            if self.newline:
                #date data contained (G*RMC)
                if self.newline.startswith("RMC", 3, 6):

                    #has date already been obtained?
                    #no
                    if self.date_flag:
                        self.state = waiting_state
                        
                    #yes date alreay obtained, so continue
                    else:
                        self.state = date_found_state
                        
                #position data contained (G*GGA)    
                elif self.newline.startswith("GGA", 3, 6):
                    self.state = position_found_state
                
                #data in uninterpretable format (covering all codes from multi-constellation GNSS)    
                elif "$GPGSA" in self.newline or \
                "$GPGSV" in self.newline or \
                "$GNGSA" in self.newline or \
                "$GNGSV" in self.newline or \
                "$GLGSA" in self.newline or \
                "$GLGSV" in self.newline:
                    self.state = waiting_state
                    
            else: 
                self.state = no_device_state
                log("No data feed from driver")

        elif self.state == date_found_state:
            
            if self.date_presence(self.newline):
                 self.state = valid_date_state
                 
            #return to wait for data
            else:
                 self.state = waiting_state 
       
       
        elif self.state == position_found_state:
            
            #are coordinates contained?
            if self.position_presence(self.newline):
                self.state = valid_position_state
                
            else:
                self.state = nofix_state
     
        elif self.state == valid_date_state:
            
            #update the system time from GPS
            self.update_time_date(self.newline)
            log("Now using GPS date and time")
            #format into readable style for logs (post sys update)
            self.format_date()
           
            self.state = waiting_state
             
        elif self.state == nofix_state:
            #process position data
            nofix = self.format_nofix(self.newline)
                
            #write out to log
            self.log_position(nofix)
            
            #send nofix coords to fifo pipe (to produce nofix sound)
            #check if pipe has already been opened
            if not self.pipe_flag: 
                self.pipe_open()
                
            #write nofix coords to pipe
            self.pipe_write_nofix()
            
            self.state = waiting_state
            
        elif self.state == valid_position_state:
            
            #process position data
            fix = self.format_position(self.newline)
            
            #write out to log
            self.log_position(fix)
            
            #check if pipe has already been opened
            if not self.pipe_flag: 
                self.pipe_open()
                
            #write lat/long to pipe
            self.pipe_write(fix)
            
            self.state = waiting_state


##############
#running code#
##############

mygpsreader = gps_reader(device_file)

log("New session started...")

while True:
    mygpsreader.update_state()
    #time.sleep(1) # remember to comment out
