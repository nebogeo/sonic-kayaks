// Sonic Kayaks Copyright (C) 2020 FoAM Kernow
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
#include <Wire.h>
#include <SoftwareSerial.h>
#include "pms7003.h"
#include "turbid.h"
#include "tempDS18.h"

const long PM_TURBID_SWITCH_TIME = 10000;
const long PM_POWER_DOWN_TIME = 1000;
const long TEMP_READ_TIME = 1000;
const long PM_MAX_ERRORS = 50; // 50 read fails @ 100ms per attempt

// globals
SoftwareSerial pmSerial(11, 12); // RX, TX
pms7003_stream pm_stream;
pms7003_packet pm_packet;
int ind_led = 3;
long pm_read_time=0;
long ds_read_time=0;
long pm_halt_time=0;
char pm_running=0;
turbid_state tstate; 

unsigned char temp_error=0;
unsigned char pm_error=0;
unsigned char pm_error_count=0;

OneWire  ds(4);  // on pin 10 (a 4.7K resistor is necessary)
byte ds_addr[12];
float current_temp;

void setup() {                
  pinMode(TURBID_LED_PIN, OUTPUT);
  pinMode(ind_led, OUTPUT);
  pinMode(13, OUTPUT);
  // Serial.begin(115200);
  
  // init the thermometer 
  ds_read_time = millis();   

  // init the turbidity sensor
  turbid_init(&tstate, 0.5);
  digitalWrite(TURBID_LED_PIN, HIGH);

  // init the air particulate matter sensor
  pms7003_stream_init(&pm_stream);
  pm_read_time = millis();   
  pm_halt_time = millis();   
  pmSerial.begin(9600);
  // wake it up, just in case
  pms7003_command cmd;
  pms7003_build_command(&cmd, pms7003_cmd_sleep, pms7003_data_sleep);
  pmSerial.write((const char *)&cmd,sizeof(cmd));
  pm_running=0;

  // init the i2c output
  Wire.begin(9);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event

  // startup complete indicator
  for (unsigned int i=0; i<10; i++) {
      digitalWrite(ind_led, HIGH);
      delay(100);
      digitalWrite(ind_led, LOW);
      delay(100);
  }  
  digitalWrite(ind_led, LOW);  
}

void loop() {
  // read the thermometer
  if (millis()-ds_read_time>TEMP_READ_TIME) {
    current_temp = ds18_finish_read_temp(ds,ds_addr);
    Wire.begin(9);                // join i2c bus with address #8
    Wire.onRequest(requestEvent); // register event    
    temp_error=0;
    temp_error=ds18_start_read_temp(ds,ds_addr);
    ds_read_time+=TEMP_READ_TIME;
  }

  if (millis()-pm_halt_time>PM_TURBID_SWITCH_TIME) {
    if (!pm_running) {
      pms7003_command cmd;
      pms7003_build_command(&cmd, pms7003_cmd_sleep, pms7003_data_wakeup);
      pmSerial.write((const char *)&cmd,sizeof(cmd));
      pm_running=1;
    } else {
      pms7003_command cmd;
      pms7003_build_command(&cmd, pms7003_cmd_sleep, pms7003_data_sleep);
      pmSerial.write((const char *)&cmd,sizeof(cmd));
      pm_running=0;      
    }
    pm_halt_time+=PM_TURBID_SWITCH_TIME;
  }
  
  // read turbidity
  if (!pm_running && millis()-pm_halt_time>PM_POWER_DOWN_TIME) {
    // don't record while the pm sensor is powered up (noise) and give it a pause to shut down properly
    // to avoid spiking
    turbid_update_constant(&tstate); 
  }

  // check for incoming pm sensor data 
  if (millis()-pm_read_time>100) {
    pm_error=0;
    digitalWrite(ind_led, LOW);
    pm_read_time+=100;
    unsigned long len=pmSerial.available();
    if (len > 0) {
      unsigned char buf[64]; 
      pmSerial.readBytes(buf,len);
      pms7003_stream_update(&pm_stream,buf,len); 
      if (pm_stream.msg_ready==1 && pm_stream.msg_size==32) {
        pm_stream.msg_ready=0;  
        pm_error_count=0;
        pm_error=0;
        // reinterpret the message as a data packet, as it's the right size
        memcpy(&pm_packet,&pm_stream.msg[0],pm_stream.msg_size);       
        digitalWrite(ind_led, HIGH);
        /*Serial.print(swap_endian(pm_packet.pmc_std_1_0));
        Serial.print(",");
        Serial.print(swap_endian(pm_packet.pmc_std_2_5));
        Serial.print(",");
        Serial.println(swap_endian(pm_packet.pmc_std_10_0));*/
      } 
    } else {
      if (pm_error_count>PM_MAX_ERRORS) {
        pm_error=1;
      }
      if (pm_running==1) pm_error_count+=1;      
    }
  }
  delay(TURBID_FLASH_MILLIS/TURBID_SAMPLES_PER_PERIOD);
}

unsigned char data_frame;

// as we can only send 32 bytes over i2c, we split it across multiple "data frames"
void requestEvent() {
  if (data_frame<3) {
    // use the first 3 reads for all the turbidity float data
    int start_sample=data_frame*3; 
    for (unsigned char i=start_sample; i<start_sample+3; i++) {
      Wire.write(i);
      Wire.write((unsigned char *)&tstate.out_sample[i].on_light,sizeof(float));
      Wire.write((unsigned char *)&tstate.out_sample[i].off_light,sizeof(float));
    }
  }
  if (data_frame==3) {
    // write the pm sensor data in the 4th read
    Wire.write((char *)&pm_packet,32);
  }
  if (data_frame==4) {
    // write the temperature value in the 5th read
    Wire.write("temp");
    Wire.write((unsigned char *)&current_temp,sizeof(float));
    Wire.write(pm_running); // write out the pm state too
    Wire.write(temp_error); 
    Wire.write(pm_error); 
  }  
  data_frame=(data_frame+1)%5;
} 
