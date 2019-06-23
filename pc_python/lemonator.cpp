#include "lemonator_proxy.hpp"

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#include "pybind11/pybind11.h"
#pragma GCC diagnostic pop

namespace py = pybind11;

PYBIND11_MODULE( lemonator, m ) {
	
   py::enum_< hwlib::buffering >( m, "buffering")
      .value( "unbuffered", hwlib::buffering::unbuffered )
      .value( "buffered", hwlib::buffering::buffered )
      .export_values();

   py::class_< output_proxy >( m, "output_proxy" ) 
      .def( "set", &output_proxy::set, "",
         py::arg("v"), py::arg("buffering") = hwlib::buffering::unbuffered );
   
   py::class_< lemonator_proxy >( m, "lemonator" )
      .def( py::init< int >() )
      .def_readonly( "led_yellow", &lemonator_proxy::p_led_yellow );
}

