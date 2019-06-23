#ifndef _LEMONATOR_HARDWARE_H
#define _LEMONATOR_HARDWARE_H

#include <algorithm>
#include "hwlib.hpp"
#include "sr04.hpp"
#include "tcs3200.hpp"
#include "ds1820.hpp"
#include "invert.hpp"
#include "lemonator_interface.hpp"

namespace target = hwlib::target;

// interface to the lemonator hardware functions
// pins are converted to active high!
class lemonator_hardware : public lemonator_interface {
private:

   // lcd
   target::pin_out lcd_rs;
   target::pin_out lcd_e;
   target::pin_out lcd_d4;
   target::pin_out lcd_d5;
   target::pin_out lcd_d6;
   target::pin_out lcd_d7;
   hwlib::port_out_from_pins lcd_data;
   hwlib::hd44780 h_lcd;
   
   // distance sensor
   target::pin_out sr04_trigger;
   target::pin_in sr04_echo;
   hwlib::sr04 h_sr04;
   
   // color sensor
   target::pin_out s0;
   target::pin_out s1;
   target::pin_out s2;
   target::pin_out s3;
   target::pin_in out;
   hwlib::port_out_from_pins s;
   hwlib::tcs3200 h_tcs3200;
   
   // keypad
   target::pin_oc out0;
   target::pin_oc out1;
   target::pin_oc out2;
   target::pin_oc out3;
   hwlib::port_oc_from_pins out_port;
   target::pin_in in0;
   target::pin_in in1;
   target::pin_in in2;
   target::pin_in in3;
   hwlib::port_in_from_pins in_port;
   hwlib::matrix_of_switches matrix;
   hwlib::keypad< 16 > h_keypad;
    
   // reflex sensor
   target::pin_in reflex_pin;
   hwlib::pin_in_invert h_reflex;
   
   // LEDs
   target::pin_out h_led_yellow_pin;
   target::pin_out h_led_green_pin;
   
   // temperature control
   target::pin_oc ds_pin;
   hwlib::ds1820 h_ds1820;
   target::pin_oc heater_pin;
   hwlib::pin_out_invert_oc h_heater;
   
   // pumps and valves
   target::pin_oc sirup_pump_pin; 
   hwlib::pin_out_invert_oc h_sirup_pump; 
   target::pin_oc water_pump_pin;
   hwlib::pin_out_invert_oc h_water_pump; 
   target::pin_oc sirup_valve_pin;
   hwlib::pin_out_invert_oc h_sirup_valve;
   target::pin_oc water_valve_pin;
   hwlib::pin_out_invert_oc h_water_valve;
   
public:

   // create interface from direct hardware access
   lemonator_hardware():
   
      lemonator_interface(
	     h_lcd,
		 h_keypad,
		 h_sr04,
		 h_tcs3200,
		 h_ds1820,
		 h_reflex,
		 h_heater,
         h_sirup_pump,
         h_sirup_valve,
         h_water_pump,
         h_water_valve,
         h_led_green_pin,
         h_led_yellow_pin
	  ),
   
         // lcd
      lcd_rs( target::pins::d53 ),
      lcd_e( target::pins::d51 ),
      lcd_d4( target::pins::d49 ),
      lcd_d5( target::pins::d47 ),
      lcd_d6( target::pins::d45 ),
      lcd_d7( target::pins::d43 ),
      lcd_data( lcd_d4, lcd_d5, lcd_d6, lcd_d7 ),
      h_lcd( lcd_rs, lcd_e, lcd_data, 4, 20 ),
   
         // distance sensor
      sr04_trigger( target::pins::d52 ),      
      sr04_echo( target::pins::d50 ),
      h_sr04( sr04_trigger, sr04_echo ),
   
         // color sensor
      s0( target::pins::d48 ),
      s1( target::pins::d46 ),      
      s2( target::pins::d44 ),      
      s3( target::pins::d42 ),      
      out( target::pins::d40 ),      
      s( s0, s1, s2, s3 ),
      h_tcs3200( s, out ),
  
         // keypad
      out0( target::pins::a0 ),
      out1( target::pins::a1 ),
      out2( target::pins::a2 ),
      out3( target::pins::a3 ),
      out_port( out0, out1, out2, out3 ),
      in0( target::pins::a4 ),
      in1( target::pins::a5 ),
      in2( target::pins::a6 ),
      in3( target::pins::a7 ),   
      in_port( in0,  in1,  in2,  in3  ),
      matrix( out_port, in_port ),
      h_keypad( matrix, "123A456B789C*0#D" ),
	  
         // reflex sensor
      reflex_pin( target::pins::a8 ),
	  h_reflex( reflex_pin ),
	  
	     // LEDs
      h_led_yellow_pin( target::pins::d41 ),
      h_led_green_pin( target::pins::d39 ),

         // temperature control
      ds_pin( target::pins::d2 ),
      h_ds1820( ds_pin ),
      heater_pin( target::pins::d3 ),
	  h_heater( heater_pin ),
  
         // pumps and valves
      sirup_pump_pin( target::pins::d8 ),
	  h_sirup_pump( sirup_pump_pin ),
      water_pump_pin( target::pins::d9 ),
	  h_water_pump( water_pump_pin ),
      sirup_valve_pin( target::pins::d10 ),
	  h_sirup_valve( sirup_valve_pin ),
      water_valve_pin( target::pins::d11 ),
	  h_water_valve( water_valve_pin )
   {}
   
};

#endif
