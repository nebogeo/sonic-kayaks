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
        dat = bus.read_i2c_block_data(I2C_addr,0)[6:10]
    except:
        dat = [0,0,0,0]
    return dat[0]

def read_temp(index):
    try:
        dat = bus.read_i2c_block_data(I2C_addr,0)[2:4]
    except:
        dat = [0,0]
    return (dat[0]+(dat[1]<<8))/16.0


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
class vfilter:
    def __init__(self):
        self.old_v = 0
        self.min_v = 9999
        self.max_v = 0
        self.norm_v = 0
        self.cur_v = 0
    
    def update(self,val):
        #gradual recalibration
        self.max_v-=0.01
        self.min_v+=0.01   
        if val>self.max_v: self.max_v=val
        if val<self.min_v: self.min_v=val
        range_v = self.max_v-self.min_v
        if range_v>0:
            self.norm_v = (val-self.min_v)/range_v
        self.old_v=self.cur_v
        self.cur_v=val

    def diff(self):
        return self.cur_v-self.old_v
    
#log("New session started...")

turbid_filter=vfilter()
temp_filter=vfilter()

while True:
    i=0
    #turbiderature reading produced
#    turbid_filter.update(read_turbid(i))
    temp_filter.update(read_temp(i))
    ##formatted and logged
    #log_turbid(combine_data(turbid_filter.cur_v,i))
    
 #   print(str(i)+":"+str(turbid_filter.cur_v))
 #   print(str(i)+" diff :"+str(turbid_filter.diff()))
 #   print(str(i)+" norm :"+str(turbid_filter.norm_v))
 #   osc.Message("/turb-"+str(i),[turbid_filter.cur_v]).sendlocal(8889)
 #   osc.Message("/turbdiff-"+str(i),[turbid_filter.diff()]).sendlocal(8889)
 #   osc.Message("/turbnorm-"+str(i),[turbid_filter.norm_v]).sendlocal(8889)

    print(str(i)+" curr :"+str(temp_filter.cur_v))
    print(str(i)+" diff :"+str(temp_filter.diff()))
    print(str(i)+" norm :"+str(temp_filter.norm_v))
    osc.Message("/temp-"+str(i),[temp_filter.cur_v]).sendlocal(8889)
    osc.Message("/tempdiff-"+str(i),[temp_filter.diff()]).sendlocal(8889)
    osc.Message("/tempnorm-"+str(i),[temp_filter.norm_v]).sendlocal(8889)


    time.sleep(1)
    
