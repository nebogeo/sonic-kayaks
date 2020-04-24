#define F_CPU F_OSC

#include <avr/io.h>
#include <util/delay.h>
#include <stdlib.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>
#include "I2C_slave.h"
#include "ds18b20.h"

#define I2C_ID 0x32

void adc_init(void) {
    // AREF = AVcc
    ADMUX = (1<<REFS0);
 
    // ADC Enable and prescaler of 128
    // 16000000/128 = 125000
    ADCSRA = (1<<ADEN)|(1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0);
}

uint16_t adc_read(uint8_t ch) {
  // select the corresponding channel 0~7
  // ANDing with ’7′ will always keep the value
  // of ‘ch’ between 0 and 7
  ch &= 0b00000111;  // AND operation with 7
  ADMUX = (ADMUX & 0xF8)|ch; // clears the bottom 3 bits before ORing
 
  // start single convertion
  // write ’1′ to ADSC
  ADCSRA |= (1<<ADSC);
 
  // wait for conversion to complete
  // ADSC becomes ’0′ again
  // till then, run loop continuously
  while(ADCSRA & (1<<ADSC));
 
  return (ADC);
}

////////////////////////////////////////////////////////

int main(void) {
  I2C_init(I2C_ID<<1); // initalize as slave with address 0x32
  adc_init();
  sei();
  
  // port C 0,1,2,3 are the analogue inputs
  // port C 4+5 is i2c

  for (int i=0; i<0xFF; i++) {
    i2cbuffer[i]=0xAF;
  }

  unsigned int count=0;

  uint8_t roma = 0;
  uint8_t romb = 0;

  while(1) {    
    i2cbuffer[0]=count;
    count++;    

    //i2cbuffer[1]=roma;
    //i2cbuffer[2]=romb;

    int temp;

    /*    if (roma==0 && romb==0) {
      ds18b20rom(&PORTD, &DDRD, &PIND, ( 1 << 0 ), &roma);
    } else {
      if (romb==0) {
	ds18b20rom(&PORTD, &DDRD, &PIND, ( 1 << 0 ), &romb);
      }
      }

    if (roma) {    
      //Start conversion (without ROM matching)
      ds18b20convert( &PORTD, &DDRD, &PIND, ( 1 << 0 ), &roma );
      //Delay (sensor needs time to perform conversion)
      _delay_ms( 1000 );
      //Read temperature (without ROM matching)
      ds18b20read( &PORTD, &DDRD, &PIND, ( 1 << 0 ), &roma, &temp );
      i2cbuffer[3]=0xff&temp;
      i2cbuffer[4]=0xff&(temp>>8);
     }
    
    if (romb) {    
      //Start conversion (without ROM matching)
      ds18b20convert( &PORTD, &DDRD, &PIND, ( 1 << 0 ), &romb );
      //Delay (sensor needs time to perform conversion)
      _delay_ms( 1000 );
      //Read temperature (without ROM matching)
      ds18b20read( &PORTD, &DDRD, &PIND, ( 1 << 0 ), &romb, &temp );
      i2cbuffer[5]=0xff&temp;
      i2cbuffer[6]=0xff&(temp>>8);
    }
    */

    //Start conversion (without ROM matching)
    ds18b20convert( &PORTD, &DDRD, &PIND, ( 1 << 0 ), NULL );
    //Delay (sensor needs time to perform conversion)
    _delay_ms( 1000 );
    //Read temperature (without ROM matching)
    ds18b20read( &PORTD, &DDRD, &PIND, ( 1 << 0 ), NULL, &temp );
    i2cbuffer[1]=0xff&temp;
    i2cbuffer[2]=0xff&(temp>>8);
        
    for (unsigned char i=0; i<4; i++) {
      i2cbuffer[i+5]=adc_read(i);
    } 

    
    _delay_ms(100);
  }
}

