import os
import glob
import time
import osc
import smbus

bus = smbus.SMBus(1)
I2C_addr = 0x32

log_path = "/home/pi/audio/audiotest/logs/turbid.log"

#record output messages to a log file
def log(text):
    adv_log = open(log_path, "a")
    adv_log.write(text + "\n")
    adv_log.close()

def read_turbid(index):
    try:
        dat = bus.read_i2c_block_data(I2C_addr,0)[2:6]
    except:
        dat = [0,0,0,0]
    return dat[0]
    
#combine turbiderature data with system time and date
def combine_data(turbid_c, index):
    dat = {"date":time.strftime("%Y:%m:%d"),
           "time":time.strftime("%H:%M:%S"),
           "device":str(i),
           "turbid":str(turbid_c)}
    return(dat)
		   
#formats a dictionary of turbiderature information and writes to the log    
def log_turbid(turbid_data):
    out = turbid_data["date"] + "," + turbid_data["time"] + "," + \
          turbid_data["device"] + "," + turbid_data["turbid"]
    log(out)

#calibration stuff for sound
old_turbids = [0]
min_turbid = 9999
max_turbid = 0

log("New session started...")
   
while True:
    i=0
    #turbiderature reading produced
    turbid_c = read_turbid(i)
    ##formatted and logged
    dat = combine_data(turbid_c,i)
    log_turbid(dat)
    
    #gradual recalibration
    max_turbid-=0.01
    min_turbid+=0.01
    
    #print("("+str(min_turbid)+" -> "+str(max_turbid)+")")
    
    if turbid_c>max_turbid: max_turbid=turbid_c
    if turbid_c<min_turbid: min_turbid=turbid_c
    
    turbid_range = max_turbid-min_turbid
    #print(str(turbid_range)+" "+str(min_turbids[i])+" "+str(max_turbids[i]))
    
    turbid_norm = 0
    if turbid_range>0:
        turbid_norm = (turbid_c-min_turbid)/turbid_range
        
    #print(str(i)+":"+str(turbid_c))
    #print(str(i)+":"+str(turbid_c-old_turbids[i]))
    #print(str(i)+" norm :"+str(turbid_norm))
    osc.Message("/turb-"+str(i),[turbid_c]).sendlocal(8889)
    osc.Message("/turbdiff-"+str(i),[turbid_c-old_turbids[i]]).sendlocal(8889)
    osc.Message("/turbnorm-"+str(i),[turbid_norm]).sendlocal(8889)
    old_turbids[i] = turbid_c

    time.sleep(1)
    
