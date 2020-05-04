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

// globals
SoftwareSerial pmSerial(11, 12); // RX, TX
pms7003_stream pm_stream;
pms7003_packet pm_packet;
int ind_led = 3;
long pm_read_time=0;
turbid_state tstate; 

void setup() {                
  pinMode(TURBID_LED_PIN, OUTPUT);
  pinMode(ind_led, OUTPUT);
  Serial.begin(115200);

  turbid_init(&tstate, 0.5);
  pms7003_stream_init(&pm_stream);
  
  pm_read_time = millis();   
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event

  pmSerial.begin(9600);

/*  pms7003_command cmd;
  pms7003_build_command(&cmd, pms7003_cmd_sleep, pms7003_data_sleep);
  Serial.println(sizeof(cmd));
  for (unsigned int i=0; i<sizeof(cmd); i++) { 
    Serial.print((((unsigned char *)(&cmd)))[i],HEX);
    Serial.print(" ");
  }
  Serial.println();
*/

    pms7003_command cmd;
    pms7003_build_command(&cmd, pms7003_cmd_sleep, pms7003_data_wakeup);
    pmSerial.write((const char *)&cmd,sizeof(cmd));
   
/*    
    delay(100);
    pms7003_build_command(&cmd, pms7003_cmd_change_mode, pms7003_data_active);
    pmSerial.write((const char *)&cmd,sizeof(cmd));
  */  

  // startup indicator
    for (unsigned int i=0; i<10; i++) {
      digitalWrite(ind_led, HIGH);
      delay(100);
      digitalWrite(ind_led, LOW);
      delay(100);
    }
    
    digitalWrite(ind_led, LOW);
    digitalWrite(TURBID_LED_PIN, LOW);

}

unsigned char pmstate=0;

float last=740;

void loop() {
  if (pmstate==0) turbid_update_constant(&tstate); 
  
 
  if (millis()-pm_read_time>100) {
    digitalWrite(ind_led, LOW);
    pm_read_time+=100;
    unsigned long len=pmSerial.available();
    if (len > 0) {
      unsigned char buf[64]; 
      pmSerial.readBytes(buf,len);
      pms7003_stream_update(&pm_stream,buf,len); 
      if (pm_stream.msg_ready==1 && pm_stream.msg_size==32) {
        pm_stream.msg_ready=0;  
        // reinterpret the message as a data packet, as it's the right size
        memcpy(&pm_packet,&pm_stream.msg[0],pm_stream.msg_size);       
        digitalWrite(ind_led, HIGH);
        Serial.print(swap_endian(pm_packet.pmc_std_1_0));
        Serial.print(",");
        Serial.print(swap_endian(pm_packet.pmc_std_2_5));
        Serial.print(",");
        Serial.println(swap_endian(pm_packet.pmc_std_10_0));
      }
    }
  } 

  delay(TURBID_FLASH_MILLIS/TURBID_SAMPLES_PER_PERIOD);
}

unsigned char data_frame;

void requestEvent() {
  if (data_frame!=3) {
    // use the first 3 reads for all the turbidity float data
    int start_sample=data_frame*3; 
    for (unsigned char i=start_sample; i<start_sample+3; i++) {
      Wire.write(i);
      Wire.write((unsigned char *)&tstate.out_sample[i].on_light,sizeof(float));
      Wire.write((unsigned char *)&tstate.out_sample[i].off_light,sizeof(float));
    }
  } else {
    // write the pm sensor data in the 4th read
    Wire.write((char *)&pm_packet,32);
  }
  data_frame=(data_frame+1)%4;
} 
