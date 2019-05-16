#ifndef _LEMONATOR_PROXY_H
#define _LEMONATOR_PROXY_H

#include "lemonator_interface.hpp"
#include "rs232.h"
#include <iostream>

class serial_port {
private:
   int p;	
   
   bool log_transactions;
   bool log_characters;
   
   void write( char c ){
      RS232_SendByte( p, c );	   
   }
   
public:
   serial_port( int p, bool log_transactions, bool log_characters ): 
      p( p ), log_transactions( log_transactions ), log_characters( log_characters )
   {
      if(RS232_OpenComport( p, 2400, "8N1" )) {
         std::cout << "Can not open comport\n" << std::flush;
         exit( 0 );
      }
   }
   
   char read(){
      unsigned char c;
      int n = RS232_PollComport( p, &c, 1 );	   
      if( n == 0 ){
		 c = '\0';
	  } else {
	     if( log_characters ){ 
		    std::cout << "{" << c << "}" << std::flush;
		 }
	  }
	  return c;
   }
   
   void write( std::string s ){
      for( auto c : s ){
         write( c );
      }		 
      if( log_characters ){
		  std::cout << "[" << s << "]\n" << std::flush;
	  }	  
   }
   
   void clear(){
      char c = 'x';
	  while( c != '\0' ){
         hwlib::wait_ms( 10 );		  
	     c = read();
	  }
   }
   
   std::string transaction( std::string s, bool response = true ){
      if( log_transactions ){
	     std::cout << "[" << s << "]" << std::flush;
      }   
	  clear();
	  write( s );	   
	  if( response ){
         std::string result = "";
		 for(;;){
            auto x = read();
            if( x == '\n' ){
			   if( log_transactions ){
			      std::cout << " => [" << result << "]\n" << std::flush;
   			   }     
               return result;			 
		    }
		    if( x != '\0' ){
               result += x;
            }			
		    if( x == '=' ){
               result = "";			 
		    }	   
		 }
      } else {
		 if( log_transactions ){
            std::cout << "\n" << std::flush;		  
	     }		
         return "";		  
	  }		  
   }
};

// generalisation of a sensor
class sensor_proxy : 
   // this is not good programming practice...
   public hwlib::sensor_temperature, 
   public hwlib::sensor_distance, 
   public hwlib::sensor_rgb,
   public hwlib::istream,
   public hwlib::pin_in
{
   serial_port & port;	
   std::string s;
   
public:
   sensor_proxy( 
      serial_port & port,
	  std::string s
   ): 
      port( port ),
	  s( s )
   {}
   
   int read_mc() override {
      auto r = port.transaction( s );
	  return std::stoi( r );
   }
   
   int read_mm() override {
      auto r = port.transaction( s );
	  return std::stoi( r );
   }
   
   rgb read_rgb() override {
      auto r = port.transaction( s );
	  return rgb( 1, 1, 1 ); // wovo
   }
   
   char getc() override {
      auto r = port.transaction( s ) + ' ';
	  auto c = r[ 0 ];
	  if( c == ' ' ){
         c = '\0';
	  }
	  return c;
   }
   
   bool get(
      hwlib::buffering buf = hwlib::buffering::unbuffered    
   ) override {
      auto r = port.transaction( s );	   
	  return r == "1";
   }
   
};	

class lcd_proxy : public hwlib::ostream {
private:	
   serial_port & port;		
public:   
   lcd_proxy( serial_port & port ): port( port ){}

   void putc( char c ){
      (void) port.transaction( std::string( "x" ) + c + "?", false );
   }
};

class output_proxy : public hwlib::pin_out {
private:	
   serial_port & port;		
   std::string s;
public:   
   output_proxy( serial_port & port, std::string s ): port( port ), s( s ){}
   
   void set(
      bool b,
	  hwlib::buffering buf = hwlib::buffering::unbuffered 
   ){
      (void) port.transaction( ( b ? "1" : "0" ) + s );
   }
};

// remote interface to the lemonator hardware functions via a serial interface
class lemonator_proxy : public lemonator_interface {
public:

   serial_port          port;
   
   lcd_proxy            p_lcd;
   sensor_proxy         p_keypad;
   sensor_proxy         p_distance;
   sensor_proxy         p_color;
   sensor_proxy         p_temperature;
   sensor_proxy         p_reflex;
   output_proxy         p_heater;
   output_proxy         p_sirup_pump;
   output_proxy         p_sirup_valve;
   output_proxy         p_water_pump;
   output_proxy         p_water_valve;
   output_proxy         p_led_green;
   output_proxy         p_led_yellow;
   
public:

   lemonator_proxy(
      int p,
	  bool log_transactions = 0,
	  bool log_characters = 0
   ):
      lemonator_interface(
	     p_lcd,
		 p_keypad,
		 p_distance,
		 p_color,
		 p_temperature,
		 p_reflex,
		 p_heater,
         p_sirup_pump,
         p_sirup_valve,
         p_water_pump,
         p_water_valve,
         p_led_green,
         p_led_yellow	  
	  ),
      port( p, log_transactions, log_characters ),
	  p_lcd( port ),
	  p_keypad( port, "z" ),
	  p_distance( port, "d" ),
	  p_color( port, "c" ),
	  p_temperature( port, "t" ),
	  p_reflex( port, "f" ),
	  p_heater( port, "h" ),
	  p_sirup_pump( port, "sp" ),
      p_sirup_valve( port, "sv" ),
      p_water_pump( port, "wp" ),
      p_water_valve( port, "wv" ),
      p_led_green( port, "g" ),
      p_led_yellow( port, "y" )
   {}	  
   
};

#endif
