
#include <Arduino.h>

const int TURBID_LED_PIN = 2;
const int TURBID_SENSOR_ANALOGUE = A0;
const long TURBID_FLASH_MILLIS=500;
const long TURBID_SAMPLES_PER_PERIOD=100;

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
void turbid_update(turbid_state *s);
void turbid_snapshot(turbid_state *s);

float filter_alpha_from_cutoff_hz(float cutoff_hz, float dt_ms);
float lowpass(float x, float last, float alpha);
