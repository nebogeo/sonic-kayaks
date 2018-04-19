import os
import glob
import time
import osc
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

log_path = "/home/pi/audio/audiotest/logs/temp.log"
device_path = "/sys/bus/w1/devices/"

#find all temperature sensors connected to pi
device_folders = glob.glob(device_path + '28*')
device_files = []
for device_folder in device_folders:
    device_files.append(device_folder + '/w1_slave')

#record output messages to a log file
def log(text):
    adv_log = open(log_path, "a")
    adv_log.write(text + "\n")
    adv_log.close()

def read_temp_raw(index):
    f = open(device_files[index], 'r')
    lines = f.readlines()
    f.close()
    return lines

#convert device reading into a readable temperature
def read_temp(index):
	lines = read_temp_raw(index)
	#YES signifies that data could be present
	while lines[0].strip()[-3:] != 'YES':
		lines = read_temp_raw(index)
	#is there a temperature reading present in the raw data?
	equals_pos = lines[1].find('t=')
	#-1 indicates no presence of tempearture, go ahead if it is present
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0 # celcius
		# temp_f = temp_c * 9.0 / 5.0 + 32.0 #fahrenheit
		return temp_c 

#combine temperature data with system time and date
def combine_data(temp_c, index):
	dat = {"date":time.strftime("%Y:%m:%d"),
        "time":time.strftime("%H:%M:%S"),
        "device":str(i),
        "temp":str(temp_c)}
	return(dat)
		   
#formats a dictionary of temperature information and writes to the log    
def log_temp(temp_data):
		out = temp_data["date"] + "," + temp_data["time"] + "," + \
		temp_data["device"] + "," + temp_data["temp"]
		log(out)

#calibration stuff for sound
old_temps = []
min_temp = 9999
max_temp = 0

for device_folder in device_folders:
    old_temps.append(0)

log("New session started...")
   
while True:
    for i in range(0,len(device_folders)):
		#temperature reading produced
		temp_c = read_temp(i)
		##formatted and logged
		dat = combine_data(temp_c,i)
		log_temp(dat)
        
        #gradual recalibration
		max_temp-=0.01
		min_temp+=0.01

		#print("("+str(min_temp)+" -> "+str(max_temp)+")")
        
		if temp_c>max_temp: max_temp=temp_c
		if temp_c<min_temp: min_temp=temp_c
        
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
