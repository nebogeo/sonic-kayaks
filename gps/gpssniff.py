# seems that the usual cat /dev/ttyXXX doesn't always work
# due to baud rates - just a simple script for sanity checking

import serial
ser = serial.Serial('/dev/ttyUSB0', 4800)

while True:
    data = ser.readline()
    if data:
        print(data)


