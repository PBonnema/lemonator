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

    std::cout << "Resetting machine..." << std::endl;

    Sleep(2000);

    while (true)
    {
        controller.update();
        Sleep(50);
    }

    return 0;
}