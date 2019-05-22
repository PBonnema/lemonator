#ifndef _LEMONATOR_DUMMY_H
#define _LEMONATOR_DUMMY_H

#include "lemonator_interface.hpp"

// generalisation of a sensor
class sensor_dummy : 
   // this is not good programming practice...
   public hwlib::sensor_temperature, 
   public hwlib::sensor_distance, 
   public hwlib::sensor_rgb,
   public hwlib::istream,
   public hwlib::pin_in
{
public:
   
   int read_mc() override {
      return 370;
   }
   
   int read_mm() override {
      return 42;
   }
   
   rgb read_rgb() override {
	  return rgb( 12, 13, 14 );
   }
   
   char getc() override {
	  return 'D';
   }
   
   bool get(
      hwlib::buffering buf = hwlib::buffering::unbuffered    
   ) override {  
	  return 1;;
   }
   
};	

class lcd_dummy : public hwlib::ostream {	
public:   
   void putc( char c ){
   }
};

class output_dummy : public hwlib::pin_out {
public:     
   void set(
      bool b,
	  hwlib::buffering buf = hwlib::buffering::unbuffered 
   ){
      // implement
   }
};

class lemonator_dummy : public lemonator_interface {
private:
   
   lcd_dummy            d_lcd;
   sensor_dummy         d_keypad;
   sensor_dummy         d_distance;
   sensor_dummy         d_color;
   sensor_dummy         d_temperature;
   sensor_dummy         d_reflex;
   output_dummy         d_heater;
   output_dummy         d_sirup_pump;
   output_dummy         d_sirup_valve;
   output_dummy         d_water_pump;
   output_dummy         d_water_valve;
   output_dummy         d_led_green;
   output_dummy         d_led_yellow;
   
public:

   lemonator_dummy():
      lemonator_interface(
	     d_lcd,
		 d_keypad,
		 d_distance,
		 d_color,
		 d_temperature,
		 d_reflex,
		 d_heater,
         d_sirup_pump,
         d_sirup_valve,
         d_water_pump,
         d_water_valve,
         d_led_green,
         d_led_yellow	  
	  ),
	  d_lcd(),
	  d_keypad(),
	  d_distance(),
	  d_color(),
	  d_temperature(),
	  d_reflex(),
	  d_heater(),
	  d_sirup_pump(),
      d_sirup_valve(),
      d_water_pump(),
      d_water_valve(),
      d_led_green(),
      d_led_yellow()
   {}	  
   
};

#endif
