import os
import glob
import time
import osc
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

log = open("temp.log","a")

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
for device_folder in device_folders:
    old_temps.append(0)

while True:
    for i in range(0,len(device_folders)):
        temp_c = read_temp(i)
        print(str(i)+":"+str(temp_c))
        print(str(i)+":"+str(temp_c-old_temps[i]))
        osc.Message("/temp",[temp_c]).sendlocal(8889)
        osc.Message("/tempdiff",[temp_c-old_temps[i]]).sendlocal(8889)
        old_temps[i] = temp_c

