#include "tempDS18.h"

void ds18_start_read_temp(OneWire &ds, byte addr[12]) {
  byte i;
  byte type_s;
  float celsius;
  
  if ( !ds.search(addr)) {
    ds.reset_search();
    //delay(250);
    //return;
  }
  
  if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      return;
  }
 
  // the first ROM byte indicates which chip
  switch (addr[0]) {
    case 0x10: // DS18S20 or old DS1820
      type_s = 1;
      break;
    case 0x28: // DS18B20
      type_s = 0;
      break;
    case 0x22: // DS1822
      type_s = 0;
      break;
    default:
      Serial.println("Device is not a DS18x20 family device.");
      return;
  } 

  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end
}

//  delay(1000);     // maybe 750ms is enough, maybe not

float ds18_finish_read_temp(OneWire &ds, byte addr[12]) {
  byte data[12];
  byte type_s = 0;

  // we might do a ds.depower() here, but the reset will take care of it.  
  ds.reset();
  ds.select(addr);    
  ds.write(0xBE);         // Read Scratchpad
  for (unsigned int i = 0; i < 9; i++) {           // we need 9 bytes
    data[i] = ds.read();
  }

  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  int16_t raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // "count remain" gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    // at lower res, the low bits are undefined, so let's zero them
    if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
    else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
    else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
    //// default is 12 bit resolution, 750 ms conversion time
  }
  return (float)raw / 16.0;
}
