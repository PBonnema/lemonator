#include "hwlib.hpp"
#include "lemonator_dummy.hpp"
#include "lemonator_server.hpp"

int main( void ){	
    
   // kill the watchdog
   WDT->WDT_MR = WDT_MR_WDDIS;
   
   // wait for the PC console to start
   hwlib::wait_ms( 1000 );
   
   auto hw = lemonator_dummy();
   auto server = lemonator_server( hw, hwlib::cout, hwlib::cin );
   server.run();
}