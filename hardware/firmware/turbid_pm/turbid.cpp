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

#include "turbid.h"

// change in time per sample (1/samplerate)
float DT_MSEC_PER_SAMPLE=(TURBID_FLASH_MILLIS/TURBID_SAMPLES_PER_PERIOD);

// precalculate from a value in hz
float filter_alpha_from_cutoff_hz(float cutoff_hz, float dt_ms) {
  float rc = 1/(2*PI*cutoff_hz);
  float dt = dt_ms/1000.0; 
  return dt/(rc+dt);    
}

// first order "infinite impulse response" low pass filter
float lowpass(float x, float last, float alpha) {
  return alpha * x + (1-alpha) * last;
}

void turbid_init(turbid_state *s, float filter_cutoff_hz) {
  s->t = millis();
  s->on_samples=0; 
  s->off_samples=0; 
  s->led_state=0;

  float alphas[NUM_TURBID_SAMPLES]= {
     1.0, // no filtering
     filter_alpha_from_cutoff_hz(20, DT_MSEC_PER_SAMPLE),
     filter_alpha_from_cutoff_hz(10, DT_MSEC_PER_SAMPLE),
     filter_alpha_from_cutoff_hz(1.0, DT_MSEC_PER_SAMPLE),
     filter_alpha_from_cutoff_hz(1/20.0, DT_MSEC_PER_SAMPLE),
     filter_alpha_from_cutoff_hz(1/50.0, DT_MSEC_PER_SAMPLE),
     filter_alpha_from_cutoff_hz(1/100.0, DT_MSEC_PER_SAMPLE),
     filter_alpha_from_cutoff_hz(1/150.0, DT_MSEC_PER_SAMPLE)
  };
  for (unsigned int i=0; i<NUM_TURBID_SAMPLES; i++) {
    s->sample[i].filter_alpha=alphas[i];
    s->sample[i].on_light=520;
    s->sample[i].off_light=0;    
  }
  turbid_snapshot(s);
}

// place a snapshot into out_samples for reading via i2c (don't want intermediate values)
void turbid_snapshot(turbid_state *s) {
  for (unsigned int i=0; i<NUM_TURBID_SAMPLES; i++) {
    s->out_sample[i].filter_alpha=s->sample[i].filter_alpha;
    s->out_sample[i].on_light=s->sample[i].on_light;
    s->out_sample[i].off_light=s->sample[i].off_light;    
  }  
}

void turbid_update_flash(turbid_state *s) {
  // sample the adc
  if (s->led_state==1) {
    int val=(1024-analogRead(TURBID_SENSOR_ANALOGUE)); 
    for (unsigned int i=0; i<NUM_TURBID_SAMPLES; i++) {    
      s->sample[i].on_light=lowpass(val,s->sample[i].on_light,s->sample[i].filter_alpha);
    }
    s->on_samples++;
  } else {
    int val=(1024-analogRead(TURBID_SENSOR_ANALOGUE));    
    for (unsigned int i=0; i<NUM_TURBID_SAMPLES; i++) {    
      s->sample[i].off_light=lowpass(val,s->sample[i].off_light,s->sample[i].filter_alpha);
    }
    s->off_samples++;
  }  
  
  // light turning on
  if (millis()-s->t>TURBID_FLASH_MILLIS && !s->led_state) {
    digitalWrite(TURBID_LED_PIN, HIGH);
    s->led_state=1;
  }
  
  // light turning off
  if (millis()-s->t>(TURBID_FLASH_MILLIS*2) && s->led_state) {
    // store all light data now
    turbid_snapshot(s);

    for (unsigned int i=2; i<8; i++) {
      Serial.print(s->out_sample[i].on_light);
      Serial.print(",");
      Serial.print(s->out_sample[i].off_light);    
      Serial.print(",");
    }  
    Serial.println("");
     
    s->on_samples=0;  
    s->off_samples=0;  
    s->t+=TURBID_FLASH_MILLIS*2;

    digitalWrite(TURBID_LED_PIN, LOW);    
    s->led_state=0;
  }
}

void turbid_update_constant(turbid_state *s) {
  // make sure the LED is on
  digitalWrite(TURBID_LED_PIN, HIGH);

  // sample the adc
  int val=(1024-analogRead(TURBID_SENSOR_ANALOGUE)); 
  for (unsigned int i=0; i<NUM_TURBID_SAMPLES; i++) {    
    s->sample[i].on_light=lowpass(val,s->sample[i].on_light,s->sample[i].filter_alpha);
  }
  s->on_samples++;

  // time to update?
  if (millis()-s->t>(TURBID_FLASH_MILLIS*2)) {
    // store all light data now
    turbid_snapshot(s);

    //for (unsigned int i=0; i<8; i++) {
    //  Serial.print(s->out_sample[0].on_light);
    //  Serial.print(",");
    //}  
    //Serial.println("");
    
    s->on_samples=0;  
    s->t=millis(); // update time to *now* logically...
  }
} 
