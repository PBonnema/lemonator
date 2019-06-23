#include "CustomController.hpp"
//#include "PrettyProgressIcon.hpp"
#include <stdio.h>
#include <stdlib.h>
#include <iostream>

int main(void)
{

    CustomController controller;
    //controller.update();
    //PrettyProgressIcon icon;

    std::cout << "Hello world" << std::endl;

    while (true)
    {
        controller.update();
        Sleep(250);
    }

    return 0;
}