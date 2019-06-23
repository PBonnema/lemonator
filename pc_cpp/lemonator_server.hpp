#ifndef _LEMONATOR_SEVER_H
#define _LEMONATOR_SEVER_H

#include "lemonator_interface.hpp"

namespace target = hwlib::target;

// serial interface to the lemonator hardware functions
class lemonator_server {
private:

   lemonator_interface  & hw;
   hwlib::ostream       & output;
   hwlib::istream       & input;
   
public:

   lemonator_server(
      lemonator_interface  & hw,
      hwlib::ostream       & output,
      hwlib::istream       & input   
   ):
      hw( hw ),
	  output( output ),
	  input( input )
   {}	  
   
   void run(){
	  bool v = 0;
	  const char * vs = "off";
	  enum class filler { water, sirup };
	  filler f = filler::water;
	  const char * fs = "water";
	  for(;;){ 
         auto c = input.getc();
	     switch( c ){
	  
		    case 't' : {
			   auto t = hw.temperature.read_mc();
		       output << "temperature=" << t << "\n";
     	       break;			   
		    }
			
            case 'd' : {
			   auto d = hw.distance.read_mm(); 
		       output << "distance=" << d << "\n";
               break;
			}
			
             case 'c' : {
			   auto d = hw.color.read_rgb(); 
		       output << "color=" << d << "\n";
               break;
			}
			
            case 'r' : {
			   auto r = hw.presence.get();
		       output << "reflex=" << r << "\n";    
               break;
			}
			
            case '1' : {
		       v = 1;
			   vs = "on";
               break;
			}
			
		    case '0' : {
		       v = 0;
			   vs = "off";
               break;
			}
			
            case 'h': {
		       output << "heater " << vs << "\n";
			   hw.heater.set( v );
			   break;
			}
			
            case 'w': {
		       f = filler::water;
			   fs = "water";
			   break;
			}
			
            case 's': {
		       f = filler::sirup;
			   fs = "sirup";
			   break;
			}
			
            case 'p': {
		       (( f == filler::water ) ? hw.water : hw.sirup ).pump.set( v );
			   output << fs << " pump " << vs << "\n";
			   break;			
			}
			
            case 'v': {
		       (( f == filler::water ) ? hw.water : hw.sirup ).valve.set( v );
			   output << fs << " valve " << vs << "\n";
			   break;						
			}
			
            case 'g': {
		       hw.led_green.set( v );
			   output << "green led " << vs << "\n";
			   break;						
			}
			
            case 'y': {
		       hw.led_yellow.set( v );
			   output << "yellow led " << vs << "\n";
			   break;						
			}
			
			case 'x' :{
			   for(;;){
				   auto c = hwlib::cin.getc();
				   if( c == '?' ){
				      break;
				   }
				   hw.lcd << c;
			   }
			   break;
			}
			
			case 'z' :{
			   auto c = hw.keypad.getc_nowait();
			   if( c == '\0' ){
                  c = ' '				   ;
			   }	  
			   output << "kbd=" << c << "\n";
               break;				
			}
			
            case ' ' : {
		       hw.sirup.pump.set( 0 );
		       hw.water.pump.set( 0 );
			   hw.heater.set( 0 );

		       hw.sirup.valve.set( 1 );
		       hw.water.valve.set( 1 );
			   hwlib::wait_ms( 500 );
		       hw.sirup.valve.set( 0 );
		       hw.water.valve.set( 0 );
			
			   output << "halt\n"; 
		       break;
            }
			   
	        default : {
               output << c << "?\n";
			   break;
	        }  		
	     }			
      }			
   }
   
};

#endif
