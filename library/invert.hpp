#ifndef _INVERT_H
#define _INVERT_H

#include "hwlib.hpp"

namespace hwlib {

class pin_in_invert : public pin_in {
private:

   pin_in & slave;
   
public:
   pin_in_invert( pin_in & slave ):
      slave( slave )
   {}	  
   
   bool get( 
      buffering buf = buffering::unbuffered 
   ){
      return ! slave.get( buf );	   
   }	
   
};

class pin_out_invert : public pin_out {
private:

   pin_out & slave;
   
public:
   pin_out_invert( pin_out & slave ):
      slave( slave )
   {}	  
   
   void set( 
      bool x,
      buffering buf = buffering::unbuffered 
   ){
      slave.set( ! x, buf );  
   }	
};

class pin_out_invert_oc : public pin_out {
private:

   pin_oc & slave;
   
public:
   pin_out_invert_oc( pin_oc & slave ):
      slave( slave )
   {}	  
   
   void set( 
      bool x,
      buffering buf = buffering::unbuffered 
   ){
      slave.set( ! x, buf );  
   }	
};

}; // namespace hwlib

#endif
