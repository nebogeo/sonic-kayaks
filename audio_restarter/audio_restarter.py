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

while True:
    if not proc_exists("jackd") or not jack_good():
        subprocess.call('./start_jack.sh', shell=True)
    time.sleep(30)


                                                            
