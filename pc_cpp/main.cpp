#include "lemonator_proxy.hpp"

int main( void ){	
   std::cout << "PC side running \n" << std::flush;
  
   // COM8 => 7, COM3 => 2
   auto hw = lemonator_proxy( 2, 0, 0 );
   
    // wait for remote to re-start after opening the com port
   hwlib::wait_ms( 4'000 );
    
   // writing to the LCD
   hw.lcd << "\fTest\nhello world"; 
   
   // blink a LED
   hwlib::blink( hw.led_yellow );
}