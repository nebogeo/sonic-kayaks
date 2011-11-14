#!/usr/bin/env python

import os
import subprocess
import time
import psutil


def proc_exists(procname):
    for proc in psutil.process_iter():
        if procname in proc.name():  
            return True
    return False

def jack_good():
    return os.system("jack_bufsize")==0

def count_xruns(fn):
    count = 0
    for line in open(fn,'r').readlines():
        if "XRun" in line:
            count+=1
    print("XRuns = "+str(count))
    return count

jack_log = "/home/pi/stick/sonickayak/logs/jackd.log"

while True:
    if (not proc_exists("jackd")) or (not jack_good()) or count_xruns(jack_log)>20:
        subprocess.call('./start_jack.sh', shell=True)
    time.sleep(10)


                                                            
