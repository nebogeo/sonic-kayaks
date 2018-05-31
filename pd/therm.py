import os
import glob
import time
import osc
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

log = open("/home/pi/audio/audiotest/logs/temp.log","a")

base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')
device_files = []
for device_folder in device_folders:
    device_files.append(device_folder + '/w1_slave')
 
def read_temp_raw(index):
    f = open(device_files[index], 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(index):
    lines = read_temp_raw(index)
    while lines[0].strip()[-3:] != 'YES':
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        log.write(time.strftime("%H:%M:%S")+" "+str(temp_c)+"\n")
        # temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

old_temps = []
min_temp = 9999
max_temp = 0

for device_folder in device_folders:
    old_temps.append(0)
        
while True:
    for i in range(0,len(device_folders)):
        temp_c = read_temp(i)

        if temp_c>max_temp: max_temp=temp_c
        if temp_c<min_temp: min_temp=temp_c

        # gradual recalibration
        #max_temps[i]*=0.99
        #min_temps[i]*=1.01
        
        temp_range = max_temp-min_temp
        #print(str(temp_range)+" "+str(min_temps[i])+" "+str(max_temps[i]))

        temp_norm = 0
        if temp_range>0:
            temp_norm = (temp_c-min_temp)/temp_range
        
        #print(str(i)+":"+str(temp_c))
        #print(str(i)+":"+str(temp_c-old_temps[i]))
        #print(str(i)+" norm :"+str(temp_norm))
        osc.Message("/temp-"+str(i),[temp_c]).sendlocal(8889)
        osc.Message("/tempdiff-"+str(i),[temp_c-old_temps[i]]).sendlocal(8889)
        osc.Message("/tempnorm-"+str(i),[temp_norm]).sendlocal(8889)
        old_temps[i] = temp_c

