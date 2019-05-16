#ifndef _HWLIB_DS1820_H
#define _HWLIB_DS1820_H

#include "hwlib.hpp"

namespace hwlib {
	
class sensor_temperature {
public:
   /// temperature in milli-celcius
   virtual int read_mc() = 0;
};	

class ds1820 : public sensor_temperature {
    hwlib::pin_oc & pin;
    
   void reset(){
      pin.set( 0 );
      hwlib::wait_us( 600 );
      pin.set( 1 );
      hwlib::wait_us( 600 );
   }  
   
   bool device_present(){
      if( ! pin.get() ) return false;
      pin.set( 0 );
      hwlib::wait_us_busy( 600 );
      pin.set( 1 );
      hwlib::wait_us_busy( 72 );
      bool presence_pulse = pin.get();
      hwlib::wait_us_busy( 600 );
      return (! presence_pulse ) && pin.get();
   }   
   
   void write( int x ){
      for( int i = 0; i < 8; i++ ){
         if( x & 0x01 ){
            pin.set( 0 );
            hwlib::wait_us_busy( 5 );
            pin.set( 1 );
            hwlib::wait_us_busy( 85 );
         } else {
            pin.set( 0 );
            hwlib::wait_us_busy( 80 );
            pin.set( 1 );
            hwlib::wait_us_busy( 20 );
         }
         x = x >> 1;
      }         
   }     
   
   unsigned char read( void ){
      unsigned char d = 0;
      for( int i = 0; i < 8; i++ ){
         d = d >> 1;
         pin.set( 0 );
         hwlib::wait_us_busy( 5 );
         pin.set( 1 );
         hwlib::wait_us_busy( 5 );
         if( pin.get() ){
            d = d | 0x80;
         }
         hwlib::wait_us_busy( 100 );
      }
      return d;
   }   
    
   void conversion_start(){
      reset();
      write( 0xCC );
      write( 0x44 );
   }   
      
public:    
    ds1820( hwlib::pin_oc & pin ):
       pin( pin )
    {
       pin.set( 1 );
    }
    
   int device_present_code(){
      if( ! pin.get() ) return 1;
      pin.set( 0 );
      if( pin.get() ) return 2;
      hwlib::wait_us_busy( 600 );
      pin.set( 1 );
      hwlib::wait_us_busy( 72 );
      bool presence_pulse = pin.get();
      hwlib::wait_us_busy( 600 );
      if( presence_pulse ) return 3;
      if( ! pin.get() ) return 4;
      return 0;
   }       
    
   int family_code(){
      if( ! device_present() ){
         return 0;
      }   
      write( 0x33 );
      hwlib::wait_us_busy( 100 );
      return read();
   }      
    
    int read_mc(){
      unsigned char d1, d2;
      conversion_start();
      hwlib::wait_ms( 800 );
      reset();
      write( 0xCC );
      write( 0xBE );
      d1 = read();
      d2 = read();
      // temp in C * 1000 for a DS18B20
      return 1000 * ((((unsigned int)d2) << 8 ) + d1 ) / 16;
    }
	
}; // class ds1820

}; // namespace hwlib

#endif


