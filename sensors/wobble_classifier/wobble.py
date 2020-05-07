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
        self.current_time=0
        self.d_avg=0
        self.d_lag=0.3    # lag to aggregate gaps/prevent steps 
        self.d_thresh=1.5 # threshold to remove noise/allow space
        self.current_event=False
        self.last_v=0
        
    def update(self,value,dt):
        event = False
        print(self.d_avg)
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
        
w=wobble()
raw_data=load_csv("/home/dave/projects/sonic-kayaks/data/20-04-06-flushing-air/pm.csv",3)
#raw_data=load_csv("/home/dave/projects/sonic-kayaks/data/20-04-28-turbid-bg/turbid-estuary-shallowswirl.csv",4)
plt_data=[]

events=[]
for i in range(825,1200): #len(raw_data)):
    v = raw_data[i]
    #if i<150: v = i
    #else: v = 300-i
    e = w.update(v,1.0)
    if e: events.append(e)
    plt_data.append(v)
    
fig = plt.figure()
ax = fig.add_subplot(111)
#ax.axes.get_yaxis().set_visible(False)
#ax.set_aspect(1)

def avg(a, b):
    return (a + b) / 2.0

print(len(events))

#################################################
# pd file export

pd_list = ""
cur_e_i = 0
for s in range(0,len(plt_data)):
    if cur_e_i<len(events) and s>=events[cur_e_i].time:
        pd_list+=events[cur_e_i].event_type+";\n"
        cur_e_i+=1
    else:
        pd_list+="none;\n"

with open("events.dat", 'w') as f:
    f.write(pd_list)

#print(pd_list)
        
#################################################
# visualisation

class viz_event:
    def __init__(self,t,begin):
        self.t=t
        self.begin=begin
        self.end=False
        
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

print(len(vevents))

for x, event in enumerate(vevents):
    x1 = [event.begin, event.end]    
    y1 = [100, 100]
    colour = "black"
    if event.t=="rise": colour='yellow'
    if event.t=="fall": colour='pink'
    plt.fill_between(x1, y1, color=colour)
    plt.text(avg(x1[0], x1[1]), 10, event.t,
             horizontalalignment='center',
             rotation=90)

line, = ax.plot(plt_data)


#plt.ylim(1, 0)
plt.show()
    
