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
#log_path = "/home/pi/stick/sonickayak/logs/turbid.csv"
log_path = "turbid.csv"

#record output messages to a log file
def log(text):
    adv_log = open(log_path, "a")
    adv_log.write(text + "\n")
    adv_log.close()


def check_pm(dat):
    if dat[0]==0x42 and dat[1]==0x4d or \
       dat[1]==0x42 and dat[0]==0x4d:
        return True
    return False

def read_arduino_block(i2c_addr,samples):
    try:
        dat = bus.read_i2c_block_data(i2c_addr,0,32)    
        if check_pm(dat):
            d = struct.unpack(">HHHHHHHHHHHHHHHH",bytearray(dat))
            samples["air"]=d
        else:
            d = struct.unpack("<BffBffBffxxxxx",bytearray(dat))
            samples[d[0]]=[d[1],d[2]]
            samples[d[3]]=[d[4],d[5]]
            samples[d[6]]=[d[7],d[8]]
        return samples
    except:
        return samples
            
def read_arduino(i2c_addr):
    samples={}
    samples=read_arduino_block(i2c_addr,samples)
    samples=read_arduino_block(i2c_addr,samples)
    samples=read_arduino_block(i2c_addr,samples)
    samples=read_arduino_block(i2c_addr,samples)
    return samples
    
log("New session started...")

i2c_addrs=[0x08,0x09] # 9 is in the box

while True:
    for dev_id,i2c_addr in enumerate(i2c_addrs):
        samples = read_arduino(i2c_addr)
        if "air" in samples: print(dev_id,samples["air"][3])
        if len(samples)==9:
            line = time.strftime("%Y:%m:%d")+","+\
                   time.strftime("%H:%M:%S")+","+str(dev_id)+","
            for sample,light_level in samples.items():
                line+=str(sample)+","+\
                       str(light_level[0])+","+\
                       str(light_level[1])+","+\
                       str(light_level[0]-light_level[1])+","
            #log(line)
            #print(line)
            #osc.Message("/turbid",[samples[0][0]-samples[0][1]]).sendlocal(8891)
    time.sleep(1)

    
