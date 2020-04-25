 
#include <Wire.h>
#include <SoftwareSerial.h>
#include "pm7003.h"
#include "turbid.h"

SoftwareSerial pmSerial(11, 12); // RX, TX

int ind_led = 4;
int ind_led_state=0;

long pmtime=0;
long pm_read_time=0;

turbid_state tstate; 

void setup() {                
  // initialize the digital pin as an output.
  pinMode(TURBID_LED_PIN, OUTPUT);
  pinMode(ind_led, OUTPUT);
  Serial.begin(115200);

  turbid_init(&tstate, 0.5);
     
  pmtime = millis();   
  pm_read_time = millis();   
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event

  pmSerial.begin(9600);

/*  pm7003_command cmd;
  pm7003_build_command(&cmd, pm7003_cmd_sleep, pm7003_data_sleep);
  Serial.println(sizeof(cmd));
  for (unsigned int i=0; i<sizeof(cmd); i++) { 
    Serial.print((((unsigned char *)(&cmd)))[i],HEX);
    Serial.print(" ");
  }
  Serial.println();
*/

    pm7003_command cmd;
    pm7003_build_command(&cmd, pm7003_cmd_sleep, pm7003_data_wakeup);
    pmSerial.write((const char *)&cmd,sizeof(cmd));
   
/*    
    delay(100);
    pm7003_build_command(&cmd, pm7003_cmd_change_mode, pm7003_data_active);
    pmSerial.write((const char *)&cmd,sizeof(cmd));
  */  
    digitalWrite(ind_led, LOW);
    digitalWrite(TURBID_LED_PIN, LOW);

}

unsigned char pmstate=0;

float last=740;

void loop() {
  if (pmstate==0) turbid_update(&tstate); 
  
  /*float v=analogRead(TURBID_SENSOR_ANALOGUE);
  last = lowpass(v,last,filter_alpha_from_cutoff_hz(0.05, 20));
  Serial.print(last);
  Serial.print(",");
  Serial.println(v);
  delay(20);
*/
  /*if (millis()-pmtime>1000) {
      pmtime+=1000;
      if (!pmstate) {
          pmstate=1;
          pm7003_command cmd;
          Serial.println("WAKE");   
          pm7003_build_command(&cmd, pm7003_cmd_sleep, pm7003_data_wakeup);
          pmSerial.write((const char *)&cmd,sizeof(cmd));
      } else {
          //Serial.println("SLEEP");   
          pmstate=0;
          pm7003_command cmd;
          pm7003_build_command(&cmd, pm7003_cmd_sleep, pm7003_data_sleep);
          //pmSerial.write((const char *)&cmd,sizeof(cmd));
      }
  }*/

  if (millis()-pm_read_time>400) {
    digitalWrite(ind_led, LOW);
    pm_read_time+=400;
    unsigned long len=pmSerial.available();
    if (len > 0) {
    Serial.print(len);
    Serial.println(" avail");   
    // max 32 bytes whatever it is (probably)
    pm7003_packet packet;
    pmSerial.readBytes((char*)&packet,len);
    if (packet.id==pm7003_id) {
      if (len==32) {
        //Serial.println("data packet recieved");   
        digitalWrite(ind_led, HIGH);
        Serial.print(swap_endian(packet.pmc_std_1_0));
        Serial.print(",");
        Serial.print(swap_endian(packet.pmc_std_2_5));
        Serial.print(",");
        Serial.println(swap_endian(packet.pmc_std_10_0));
      } else {
        Serial.println("something else recieved"); 
        for (unsigned int i=0; i<len; i++) { 
          Serial.print((((unsigned char *)(&packet)))[i],HEX);
          Serial.print(" ");
        }
        Serial.println();           
      }
    }
  }
  }  


  delay(TURBID_FLASH_MILLIS/TURBID_SAMPLES_PER_PERIOD);
}

void requestEvent() {
  Wire.write(0xab);
  Wire.write(0xcd);
  /*Wire.write(tstate.out_on_light);
  Wire.write(tstate.out_off_light);
  Wire.write(tstate.out_on_samples);
  Wire.write(tstate.out_off_samples);*/
} 
