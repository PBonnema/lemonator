#ifndef _LEMONATOR_INTERFACE_H
#define _LEMONATOR_INTERFACE_H

#include <algorithm>
#include "hwlib.hpp"
#include "sr04.hpp"
#include "tcs3200.hpp"
#include "ds1820.hpp"

// all bool interfaces are active high

// interface to a filler (= a pump/valve combination)
class filler {
public:

   hwlib::pin_out & pump;
   hwlib::pin_out & valve;
	
   filler(
      hwlib::pin_out & pump,
	  hwlib::pin_out & valve
   ):
      pump( pump ), 
      valve( valve )
   {}	  
   
};

// abstract interface to the lemonator hardware functions
class lemonator_interface {
public:

   hwlib::ostream                & lcd;
   hwlib::istream                & keypad; 
   
   hwlib::sensor_distance        & distance;
   hwlib::sensor_rgb             & color;
   hwlib::sensor_temperature     & temperature;
   hwlib::pin_in                 & presence;
   
   hwlib::pin_out                & heater;
   hwlib::pin_out                & sirup_pump;
   hwlib::pin_out                & sirup_valve;
   hwlib::pin_out                & water_pump;
   hwlib::pin_out                & water_valve;
   hwlib::pin_out                & led_green;
   hwlib::pin_out                & led_yellow;

   filler                        sirup;
   filler                        water;
	
   lemonator_interface(
      hwlib::ostream                & lcd,
      hwlib::istream                & keypad,
   
      hwlib::sensor_distance        & distance,
      hwlib::sensor_rgb             & color,
      hwlib::sensor_temperature     & temperature,
      hwlib::pin_in                 & presence,
   
      hwlib::pin_out                & heater,
      hwlib::pin_out                & sirup_pump,
      hwlib::pin_out                & sirup_valve,
      hwlib::pin_out                & water_pump,
      hwlib::pin_out                & water_valve,
      hwlib::pin_out                & led_green,
      hwlib::pin_out                & led_yellow
   ):
      lcd ( lcd ),
      keypad ( keypad ),
   
      distance( distance ),
      color( color ),
      temperature( temperature ),
      presence( presence ),
   
      heater( heater ),
      sirup_pump( sirup_pump ),
      sirup_valve( sirup_valve ),
      water_pump( water_pump ),
      water_valve( water_valve ),
      led_green( led_green ),
      led_yellow( led_yellow ), 
   
      sirup( sirup_pump, sirup_valve ),
	  water( water_pump, water_valve )
   {}	  
	 
};

#endif
