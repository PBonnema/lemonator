#ifndef _HWLIB_SR04_H
#define _HWLIB_SR04_H

#include "hwlib.hpp"

namespace hwlib {
	
class sensor_distance {
public:
   /// distance in mm
   virtual int read_mm() = 0;
};	

class sr04 : public sensor_distance {
   pin_out & trigger;
   pin_in  & echo;
   
public:
   sr04( pin_out & trigger, pin_in & echo ): 
      trigger( trigger ), echo( echo )
   {
      trigger.set( 0 ); 
   }
   
   int read_us(){
      trigger.set( 1 );
      wait_us( 10 );
      trigger.set( 0 );
      auto t = now_us();
      while( ! echo.get() ){
         if( now_us() > ( t + 100'000 ) ){
            return 0;
         }
      }
      auto start = now_us();
      while( echo.get() ){
      }
      auto end = now_us();
      return end - start;
   }
   
   int read_mm(){   
      return ( 10 * read_us())  / 84;
   }
      
}; // class sr04

}; // namespace hwlib

#endif