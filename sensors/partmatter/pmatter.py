import serial
import struct
import time

class pm_packet:
    def __init__(self,raw):
        f = struct.unpack(">HHHHHHHHHHHHHHHH",raw)
        self.time=time.time()
        self.sig=f[0]
        self.frame_len=f[1]
        self.pmc_std={"1.0":f[2],
                      "2.5":f[3],
                      "10.0":f[4]}
        self.pmc_env={"1.0":f[5],
                      "2.5":f[6],
                      "10.0":f[7]}
        self.np={"0.3":f[8],
                 "0.5":f[9],
                 "1.0":f[10],
                 "2.5":f[11],
                 "5.0":f[12],
                 "10.0":f[13]}
        self.res=f[14]
        self.checksum=f[15]

    def to_str(self):
        ret=""
        ret+="frame_len: "+str(self.frame_len)+"\n"
        ret+="pm concentration standard: \n"
        names=["1.0","2.5","10.0"]
        for d in names:
            ret+=d+": "+str(self.pmc_std[d])+"\n"
        ret+="\npm concentration environ: \n"
        for d in names:
            ret+=d+": "+str(self.pmc_env[d])+"\n"
        ret+="\nparticle size counts: \n"
        names=["0.3","0.5","1.0","2.5","5.0","10.0"]
        for d in names:
            ret+=d+": "+str(self.np[d])+"\n"
        return ret
 
    def to_csv(self):
        ret=str(self.time)+", "
        names=["1.0","2.5","10.0"]
        for d in names:
            ret+=str(self.pmc_std[d])+", "
        for d in names:
            ret+=str(self.pmc_env[d])+", "
        names=["0.3","0.5","1.0","2.5","5.0","10.0"]
        for d in names:
            ret+=str(self.np[d])+", "
        ret+="\n"
        return ret
    
sensor=serial.Serial("/dev/ttyS0")

while True:
    p = pm_packet(sensor.read(32))
    f = open("pm.csv","a")
    print(p.to_str())
    f.write(p.to_csv())
    f.close()
