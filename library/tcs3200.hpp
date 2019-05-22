#ifndef _HWLIB_TCS3200_H
#define _HWLIB_TCS3200_H

#include "hwlib.hpp"

namespace hwlib {
	
class sensor_rgb {
public:

   struct rgb {
      int r, g, b;
      rgb( int r, int g, int b ): r( r ), g( g ), b( b ){}
   };
   
   template< typename T >
   friend T & operator<<( T & cout, const rgb & c ){
      return cout << "(" << c.r << "," << c.g << "," << c.b << ")";
   }
   
   /// return the color as 3 precentages
   virtual rgb read_rgb() = 0;

};   
   
class tcs3200 : public sensor_rgb {
   port_out & s;
   pin_in   & out;
   
public:
   tcs3200( port_out & s, pin_in &out ): 
      s( s ), out( out )
   {
      s.set( 0 );
   }
   
   int read_channel( int ch ){
      s.set( ch );
      auto t = now_us() + 10'000;
      int count = 0;	  
	  bool last = 0;
	  while( now_us() < t ){
         auto next = out.get();
         if( last != next ){
            ++count;
            last = next;		 
         }   
      }
      s.set( 0 );
	  return count;
   }
   
   rgb read_rgb(){
      const int mode = 1;       
      auto r = read_channel( mode + ( 0 << 2 ));
      auto b = read_channel( mode + ( 2 << 2 ));
      // auto w = read_channel( mode + ( 1 << 2 ));
      auto g = read_channel( mode + ( 3 << 2 ));
      // cout << w << " " << r << " " << g << " " << b << "\n";
      
      auto t = r + g + b;
      return rgb( 
         ( 100 * r ) / t,
         ( 100 * g ) / t,
         ( 100 * b ) / t );
   }
     
}; // class tcs3200

}; // namespace hwlib

#endif
