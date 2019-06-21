#pragma once
#include <String>
#include <cctype>
#include "lemonator_proxy.hpp"


struct Constants
{
    const float levelVoltageFactor = 625.0;
    const float liquidMax = 2000.0;
};


enum class States: int {
    IDLE,
    WAITING_FOR_CUP,
    WAITING_USER_SELECTION_ONE,
    DISPENSING_WATER,
    DISPENSING_SIRUP,
    DISPENSING_DONE,
    DISPENSING_FAULT,
    DISPLAY_STATS,
    WAITING_USER_SELECTION_TWO,
    WAITING_USER_HEAT_SELECTION
};

enum class Faults: int {
    DISPENSING_CUP_REMOVED,
    DISPENSING_CUP_OVERFLOW,
    DISPENSING_WATER_SHORTAGE,
    DISPENSING_SIRUP_SHORTAGE,
    SELECTION_TEMP_TOO_HIGH,
    SELECTION_FLUID_TOO_HIGH,
    SELECTION_INVALID,
    NONE
};



class CustomController
{
private:

    //int COM = 2;

    
    States state;
    Faults fault;
    /* Effector waterPump;
    Effector sirupPump;
    Effector waterValve;
    Effector sirupValve;
    Effector heater;

    Sensor colour;
    Sensor temperature;
    Sensor level;
    Sensor cup;

    LEDGreen LedGreen;
    LEDYellow LedYellow;
    
    LCD lcd;
    
    Keypad keypad;*/

    Constants constants;

    lemonator_proxy proxy;

    float beginLevelCup;
    float currentLevelCup;
    float liquidLevelWater;
    float liquidLevelSirup;

    
    std::string inputTargetLevelWater;
    std::string inputTargetLevelSirup;
    std::string targetHeat;

    char latestKeypress;


    
public:
    //CustomController(Effector waterPumpObject, Effector sirupPumpObject, Effector waterValveObject, Effector sirupValveObject, Effector heaterObject, 
    //Sensor tempratureObject, Sensor levelObject, Sensor cupObject, LEDGreen LedGreenObject, LEDYellow LedYellowObject, LCD lcdObject, Keypad keypadObject);
    CustomController();
    ~CustomController(void);
    
    void update(void);
    void idleState(void);
    void waitingForCupState(void);
    void enterSelectionOneState(void);
    void enterSelectionTwoState(void);
    void enterheatSelectionState(void);
    void dispensingWaterState(void);
    void dispensingSirupState(void);
    void displayStatsState(void);
    void displayFault(Faults fault);
    void heaterOnTemp(int targetTemperature);
    void startWaterPump(void);
    void startSirupPump(void);
    bool validateCupApperance(void);
    void shutFluids(void);
    void updateLeds(void);
    void updateDisplay(void);



};
