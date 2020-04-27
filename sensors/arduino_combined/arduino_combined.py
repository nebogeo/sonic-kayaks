import os
import glob
import time
import osc
import smbus
import struct

class auto_cali:
    def __init__(self):
        self.mini = 9999
        self.maxi = 0

    def update(self,v):
        #gradual recalibration
        self.maxi-=0.01
        self.mini+=0.01
        if v>self.maxi: self.maxi=v
        if v<self.mini: self.mini=v    
        r = float(self.maxi-self.mini)
        print(str(r)+" "+str(self.mini)+" "+str(self.maxi))            
        if r>0:
            return (v-self.mini)/r
        else:
            return 0

# reads the turbidity and particulate matter
# from the arduino, logs it and sends it to pure data

bus = smbus.SMBus(1)
I2C_addr = 0x08

log_path = "/home/pi/audio/audiotest/logs/turbid.csv"

num_turbid_samples=8
turbid_sample_size=4*3 # sizeof float * 3 readings

#record output messages to a log file
def log(text):
    adv_log = open(log_path, "a")
    adv_log.write(text + "\n")
    adv_log.close()

def read_arduino():
    samples={0:[99,99],1:[99,99],2:[99,99],3:[99,99],
             4:[99,99],5:[99,99],6:[99,99],7:[99,99]}
    try:
        dat = bus.read_i2c_block_data(I2C_addr,0,32)    
        d = struct.unpack("<BffBffBffxxxxx",bytearray(dat))
        samples[d[0]]=[d[1],d[2]]
        samples[d[3]]=[d[4],d[5]]
        samples[d[6]]=[d[7],d[8]]
        dat = bus.read_i2c_block_data(I2C_addr,0,32)    
        d = struct.unpack("<BffBffBffxxxxx",bytearray(dat))
        samples[d[0]]=[d[1],d[2]]
        samples[d[3]]=[d[4],d[5]]
        samples[d[6]]=[d[7],d[8]]
        dat = bus.read_i2c_block_data(I2C_addr,0,32)    
        d = struct.unpack("<BffBffBffxxxxx",bytearray(dat))
        samples[d[0]]=[d[1],d[2]]
        samples[d[3]]=[d[4],d[5]]
        samples[d[6]]=[d[7],d[8]]
    except:
        pass
    return samples
    
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

#log("New session started...")

while True:
    samples = read_arduino()
    #for sample,lights in read_arduino().items():
    #print(sample,lights)
    print(samples[0][0]-samples[0][1])
    osc.Message("/turbid",[samples[0][0]-samples[0][1]]).sendlocal(8891)

    time.sleep(1)

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
        
    print(str(i)+":"+str(turbid_c))
    print(str(i)+":"+str(turbid_c-old_turbids[i]))
    print(str(i)+" norm :"+str(turbid_norm))
    osc.Message("/turb-"+str(i),[turbid_c]).sendlocal(8889)
    osc.Message("/turbdiff-"+str(i),[turbid_c-old_turbids[i]]).sendlocal(8889)
    osc.Message("/turbnorm-"+str(i),[turbid_norm]).sendlocal(8889)
    old_turbids[i] = turbid_c

    time.sleep(1)
    
