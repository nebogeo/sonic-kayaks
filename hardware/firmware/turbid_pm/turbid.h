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

// just for A0, probably
#include <Arduino.h>

#ifndef KAYAKS_TURBIDITY
#define KAYAKS_TURBIDITY

const int TURBID_LED_PIN = 2;
const int TURBID_SENSOR_ANALOGUE = A0;
const char TURBID_FLASH_MODE=0;
const long TURBID_FLASH_MILLIS=100;
const long TURBID_SAMPLES_PER_PERIOD=20;

struct turbid_sample {
  float filter_alpha;
  float on_light;
  float off_light;
};

const unsigned int NUM_TURBID_SAMPLES=8;

struct turbid_state {
  long t;
  turbid_sample sample[NUM_TURBID_SAMPLES];
  long on_samples; 
  long off_samples; 
  int led_state;
  turbid_sample out_sample[NUM_TURBID_SAMPLES];
  int out_on_samples;
  int out_off_samples;
};

void turbid_init(turbid_state *s, float filter_cutoff_hz);

// Flash mode alternates between the light on and off so we can compare 
// the difference. This turns out to be more useful for testing light levels than 
// normal operation, as it the difference between them will decrease due
// to turbidity as well as light entering the tube.
// With flashing there is also a problem with how long LDRs take to respond 
// to light level changes.
void turbid_update_flash(turbid_state *s);
// Use this for measurement - and ignore off_light in samples
void turbid_update_constant(turbid_state *s);
void turbid_snapshot(turbid_state *s);

float filter_alpha_from_cutoff_hz(float cutoff_hz, float dt_ms);
float lowpass(float x, float last, float alpha);

#endif
