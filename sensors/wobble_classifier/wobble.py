import csv
import sys
import matplotlib.pyplot as plt
import numpy as np

def load_csv(file,col):
    the_list = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            the_list.append(int(row[col]))
    return the_list

class wobble_event:
    def __init__(self,event_type,value,time):
        self.event_type=event_type
        self.value=value
        self.time=time
    def pprint(self):
        print(self.event_type+" "+str(self.value)+" "+str(self.time))
        
class wobble:
    def __init__(self):
        self.lowest=9999
        self.highest=-9999
        self.current_time=0
        self.state="rise"
        self.last_v=0
        self.v_avg=0
        self.v_lag=0.01
        self.v_thresh=40
        self.d_avg=0
        self.d_lag=0.2
        self.d_thresh=3
        self.time_since_risefall=0
        
    def update(self,value,dt):
        events=[]
        #if value<self.lowest:
        #    self.lowest=value
        #    events.append(wobble_event("lowest",v,self.current_time))
        #if value>self.highest:
        #    self.highest=value
        #    events.append(wobble_event("highest",v,self.current_time))
        
        delta = value-self.last_v
        if self.time_since_risefall>=0:
            if delta>(self.d_avg+self.d_thresh): 
                events.append(wobble_event("rise",delta,self.current_time))
                self.time_since_risefall=0
            if delta<(self.d_avg-self.d_thresh): 
                events.append(wobble_event("fall",delta,self.current_time))
                self.time_since_risefall=0
        self.time_since_risefall+=dt
        
        new_state=self.state # so is static is whatever the direction is
        if value<(self.v_avg-self.v_thresh): new_state="fall"
        if value>(self.v_avg+self.v_thresh): new_state="rise"

        # change in direction after a while = peak/trough
        #if self.state!=new_state:
        #    if self.state=="rise":
        #        events.append(wobble_event("peak",v,self.current_time))
        #    if self.state=="fall":
        #        events.append(wobble_event("trough",v,self.current_time))

        # change in direction after a while = peak/trough
        if self.state!=new_state:
            if self.state=="rise":
                events.append(wobble_event("peak",v,self.current_time))
            if self.state=="fall":
                events.append(wobble_event("trough",v,self.current_time))

        if value>(self.v_avg+self.v_thresh): 
            events.append(wobble_event("high",value,self.current_time))
        if value<(self.v_avg-self.v_thresh): 
            events.append(wobble_event("low",value,self.current_time))
                
        self.state=new_state
        self.current_time+=dt
        self.last_v=value
        self.d_avg=self.d_avg*(1-self.d_lag)+delta*self.d_lag
        self.v_avg=self.v_avg*(1-self.v_lag)+value*self.v_lag
        return events
        
w=wobble()
raw_data=load_csv("/home/dave/projects/sonic-kayaks/data/20-04-06-flushing-air/pm.csv",3)
#raw_data=load_csv("/home/dave/projects/sonic-kayaks/data/20-04-28-turbid-bg/turbid-estuary-shallowswirl.csv",4)
plt_data=[]

events=[]
for i in range(800,1000): #len(raw_data)):
    v = raw_data[i]
    #if i<150: v = i
    #else: v = 300-i
    events+=w.update(v,1.0)
    plt_data.append(v)
    
fig = plt.figure()
ax = fig.add_subplot(111)
#ax.axes.get_yaxis().set_visible(False)
#ax.set_aspect(1)

def avg(a, b):
    return (a + b) / 2.0

for x, event in enumerate(events):
    event.pprint()
    x1 = [event.time-1, event.time+1]    
    y1 = [100, 100]
    if event.event_type == "rise":
        plt.fill_between(x1, y1, color='yellow')
    if event.event_type == "fall":
        plt.fill_between(x1, y1, color='blue')
    if event.event_type == "high":
        plt.fill_between(x1, y1, color='red')
    if event.event_type == "low":
        plt.fill_between(x1, y1, color='green')
    plt.text(avg(x1[0], x1[1]), 10, event.event_type+" {:.2f}".format(event.value),
             horizontalalignment='center',
             rotation=90)

line, = ax.plot(plt_data)


#plt.ylim(1, 0)
plt.show()
    
