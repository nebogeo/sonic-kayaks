import csv
import sys
import matplotlib.pyplot as plt
import numpy as np

def load_csv(file,col):
    the_list = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            the_list.append(float(row[col]))
    return the_list

def avg(a, b):
    return (a + b) / 2.0

class wobble_event:
    def __init__(self,event_type,value,time):
        self.event_type=event_type
        self.value=value
        self.time=time
    def pprint(self):
        print(self.event_type+" "+str(self.value)+" "+str(self.time))
        
class wobble:
    def __init__(self,lag,thresh):
        self.current_time=0
        self.d_avg=0
        self.d_lag=lag        # lag to aggregate gaps/prevent steps 
        self.d_thresh=thresh  # threshold to remove noise/allow space
        self.current_event=False
        self.last_v=0
        
    def update(self,value,dt):
        event = False
        if self.current_event==False:
            # detect start of an event
            if self.d_avg>self.d_thresh: 
                event=wobble_event("rise begin",value,self.current_time)
                self.current_event=event
            if self.d_avg<-self.d_thresh: 
                event=wobble_event("fall begin",value,self.current_time)
                self.current_event=event
        else:
            # detect end of the current event
            event_type=self.current_event.event_type
            if event_type=="rise begin" and self.d_avg<0: 
                event=wobble_event("rise end",value,self.current_time)
                self.current_event=False
            if event_type=="fall begin" and self.d_avg>0: 
                event=wobble_event("fall end",value,self.current_time)
                self.current_event=False
                
        self.current_time+=dt        
        self.d_avg=self.d_avg*(1-self.d_lag)+(value-self.last_v)*self.d_lag
        self.last_v=value
        return event

    def finish(self,value):
        event = False
        if self.current_event!=False:
            event_type=self.current_event.event_type
            if event_type=="rise begin": 
                event=wobble_event("rise end",value,self.current_time)
                self.current_event=False
            if event_type=="fall begin": 
                event=wobble_event("fall end",value,self.current_time)
                self.current_event=False
        return event
    
#################################################
# pd file export

def pd_export(slices):
    pd_list = ""
    cur_e_i = []
    for slice in slices:
        cur_e_i.append(0)
    # assume all same size
    for s in range(0,len(slices[0].plt_data)):
        for i,slice in enumerate(slices):
            pd_list+=str(slice.raw[s%len(slice.raw)])+" "
            if cur_e_i[i]<len(slice.events) and s>=slice.events[cur_e_i[i]].time:
                pd_list+=slice.events[cur_e_i[i]].event_type.replace(" ","-")+" "
                cur_e_i[i]+=1
            else:
                pd_list+="none "
        pd_list+=";\n"

    with open("sensors.dat", 'w') as f:
        f.write(pd_list)

####################################################
    
class data_slice:
    def __init__(self,csv,col,mini,length,offset,lag,thresh):
        self.raw=load_csv(csv,col)[offset:length+offset]
        self.classifier=wobble(lag,thresh)
        self.plt_data=[]
        self.events=[]
        pos=0
        v=0
        # pre-run the classifier - todo:why
        for i in range(0,100):
            self.classifier.update(self.raw[0]-mini,0.0)
        for i in range(0,length):
            if pos>=len(self.raw): pos=0
            v = self.raw[pos]-mini
            e = self.classifier.update(v,1.0)
            if e: self.events.append(e)
            self.plt_data.append(v)
            pos+=1
        e = self.classifier.finish(v)
        if e: self.events.append(e)

#################################################
# visualisation

class viz_event:
    def __init__(self,t,begin):
        self.t=t
        self.begin=begin
        self.end=False
        
def viz_events(events):
    vevents = []
    state = False
    cur_ve = False
    for x, event in enumerate(events):
        if cur_ve==False:
            if event.event_type=="rise begin":
                cur_ve=viz_event("rise",event.time)
            if event.event_type=="fall begin":
                cur_ve=viz_event("fall",event.time)
        else:
            if event.event_type=="rise end":
                cur_ve.end=event.time
                vevents.append(cur_ve)
                cur_ve=False
            if event.event_type=="fall end":
                cur_ve.end=event.time
                vevents.append(cur_ve)
                cur_ve=False
    return vevents

def plot_vevents(vevents,height):
    for x, event in enumerate(vevents):
        x1 = [event.begin, event.end]    
        y1 = [height, height]
        colour = "black"
        if event.t=="rise": colour='yellow'
        if event.t=="fall": colour='pink'
        plt.fill_between(x1, y1, color=colour)
        plt.text(avg(x1[0], x1[1]), 10, event.t,
                 horizontalalignment='center',
                 rotation=90)
        
#################################################
            
path = "/home/dave/projects/sonic-kayaks/data/"
length = 120

#temp_data=data_slice(path+"20-04-06-flushing-air/temp-singlesensor.log",3,0,length,1000,0.1,0.03)
#pm25_data=data_slice(path+"20-04-06-flushing-air/pm.csv",3,0,length,500,0.3,1.5)
#turbid_data=data_slice(path+"20-04-28-turbid-bg/turbid-estuary-riverflow.csv",4,700,length,0,0.3,4)

temp_data=data_slice("../fake/fake-sensors.csv",0,0,length,0,0.1,0.03)
pm25_data=data_slice("../fake/fake-sensors.csv",1,0,length,0,0.3,1.5)
turbid_data=data_slice("../fake/fake-sensors.csv",2,700,length,0,0.3,4)

pd_export([temp_data,pm25_data,turbid_data])

fig = plt.figure()
ax = fig.add_subplot()
#ax.axes.get_yaxis().set_visible(False)
#ax.set_aspect(1)

plot_vevents(viz_events(temp_data.events),20)
#plot_vevents(viz_events(pm25_data.events),100)
#plot_vevents(viz_events(turbid_data.events),300)

ax.plot(temp_data.plt_data,label="temp")
ax.plot(pm25_data.plt_data,label="pm2.5")
ax.plot(turbid_data.plt_data,label="turbid")

plt.xlabel('time seconds')
plt.legend()
plt.show()
    
