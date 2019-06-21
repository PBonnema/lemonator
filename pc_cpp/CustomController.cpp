#include "CustomController.hpp"



CustomController::CustomController(Effector waterPumpObject, Effector sirupPumpObject, Effector waterValveObject, Effector sirupValveObject, Effector heaterObject, 
    Sensor tempratureObject, Sensor levelObject, Sensor cupObject, LEDGreen LedGreenObject, LEDYellow LedYellowObject, LCD lcdObject, Keypad keypadObject):
    waterPump(waterPumpObject), sirupPump(sirupPumpObject), waterValve(waterValveObject), sirupValve(sirupValveObject), heater(heaterObject), temperature(tempratureObject),
    level(levelObject), LedGreen(LedGreenObject), LedYellow(LedYellowObject), lcd(lcdObject), keypad(keypadObject), boi(2)
{
    state = States::IDLE;
    fault = Faults::NONE;
    beginLevelCup = 0.0;
    currentLevelCup = beginLevelCup;
    liquidLevelWater = constants.liquidMax;
    liquidLevelSirup = constants.liquidMax;
    
    inputTargetLevelWater = "";
    inputTargetLevelSirup = "";
    targetHeat = "";
}

void CustomController::update(){
    latestKeypress = keypad.pop();
    lcd.clear();

    if(std::stoi(targetHeat) != 0 && state != States::WAITING_USER_HEAT_SELECTION){
        heaterOnTemp(std::stoi(targetHeat));
    }

    if(waterPump.isOn() || sirupPump.isOn()){
        if(liquidLevelWater <= 0.0){
            shutFluids();
            fault = Faults::DISPENSING_WATER_SHORTAGE;
        }
        if(liquidLevelSirup <= 0.0){
            shutFluids();
            fault = Faults::DISPENSING_SIRUP_SHORTAGE;
        }
    } 

    if(fault != Faults::NONE){
        displayFault(fault);
        return;
    }

    lcd.pushString("\x0c   Lemonator v1.0\n--------------------\n");

    switch (state)
    {
    case States::IDLE:
        idleState();
        break;
    case States::WAITING_FOR_CUP:
        waitingForCupState();
        break;
    case States::WAITING_USER_SELECTION_ONE:
        enterSelectionOneState();
        break;
    case States::WAITING_USER_SELECTION_TWO:
        enterSelectionTwoState();
        break;
    case States::WAITING_USER_HEAT_SELECTION:
        enterheatSelectionState();
        break;
    case States::DISPENSING_WATER:
        dispensingWaterState();
        break;
    case States::DISPENSING_SIRUP:
        dispensingSirupState();
        break;
    case States::DISPLAY_STATS:
        displayStatsState();
    default:
        break;
    };
}

void CustomController::idleState(void){
    lcd.pushString("A = Start, B = Stats\n     C = Heat");

    switch (latestKeypress)
    {
    case 'A':
        inputTargetLevelWater = "";
        inputTargetLevelSirup = "";
        beginLevelCup = level.readValue();
        currentLevelCup = beginLevelCup;
        break;
    case 'B':
        state = States::DISPLAY_STATS;
        break;
    case 'C':
        targetHeat = "";
        state = States::WAITING_USER_HEAT_SELECTION;
    default:
        fault = Faults::SELECTION_INVALID;
        break;
    }
}

void CustomController::waitingForCupState(void){
    if(cup.readValue()){
        state = States::WAITING_USER_SELECTION_ONE;
    }else{
        lcd.pushString("Please place a cup\nto continue...\n");
    }
}

void CustomController::enterSelectionOneState(void){
    lcd.pushString("Water: " + inputTargetLevelWater);
    
    if(isdigit(latestKeypress)){
        lcd.putc(latestKeypress);
        inputTargetLevelWater += latestKeypress;
    }

    lcd.pushString("ml (#)\n");
    lcd.pushString("Sirup: " + inputTargetLevelSirup + "ml");

    if(latestKeypress == '#'){
        if(std::stoi(inputTargetLevelWater) < 0){
            fault = Faults::SELECTION_INVALID;
        }

        if(std::stoi(inputTargetLevelWater) > liquidLevelWater){
            fault = Faults::DISPENSING_WATER_SHORTAGE;
        }else{
            state = States::WAITING_USER_SELECTION_TWO;
        }
    }
}
        
void CustomController::enterSelectionTwoState(void){
    lcd.pushString("Water: " + inputTargetLevelWater + "ml\n");
    lcd.pushString("Sirup: " + inputTargetLevelSirup);

        if(isdigit(latestKeypress)){
            lcd.putc(latestKeypress);
            inputTargetLevelSirup += latestKeypress;
        }
    
    lcd.pushString("ml (#)");

    if(latestKeypress == '#'){
        if(std::stoi(inputTargetLevelSirup) < 0){
            fault = Faults::DISPENSING_SIRUP_SHORTAGE;
        }

        if(std::stoi(inputTargetLevelSirup) > liquidLevelSirup){
            fault = Faults::DISPENSING_SIRUP_SHORTAGE;
        }else{
            state = States::DISPENSING_WATER;
        }
    }
}

void CustomController::enterheatSelectionState(void){
    lcd.pushString("Heat: " + targetHeat);

    if (isdigit(latestKeypress)){
        lcd.putc(latestKeypress);
        targetHeat += latestKeypress;
    }

    lcd.pushString(" °C (#)");

    if(latestKeypress == '#'){
        if(std::stoi(targetHeat) < 0){
            fault = Faults::SELECTION_INVALID;
        }else if(std::stoi(targetHeat) >= 100){
            fault = Faults::SELECTION_TEMP_TOO_HIGH;
        }else{
            state = States::IDLE;
        }
    }
    
}

void CustomController::dispensingWaterState(void){
    if(validateCupApperance()){
        startWaterPump();
        updateDisplay();
    
        if(((level.readValue() - currentLevelCup)*constants.levelVoltageFactor) - std::stoi(inputTargetLevelWater) >= 0){
            shutFluids();
            currentLevelCup = level.readValue();
            liquidLevelWater -= std::stoi(inputTargetLevelWater);
            state = States::DISPENSING_SIRUP;
        }
    }
}

void CustomController::dispensingSirupState(void){
    if(validateCupApperance()){
        startSirupPump();
        updateDisplay();
    
        if(((level.readValue() - currentLevelCup)*constants.levelVoltageFactor) - std::stoi(inputTargetLevelSirup) >= 0){
            shutFluids();
            currentLevelCup = level.readValue();
            liquidLevelSirup -= std::stoi(inputTargetLevelSirup);
            state = States::IDLE;
        }
    }
}

void CustomController::displayStatsState(void){
    lcd.pushString(std::to_string(liquidLevelWater) + "ml <|> ");
    lcd.pushString(std::to_string(liquidLevelSirup) + "ml\n");
    lcd.pushString("Press \'#\' to exit.");

    if(latestKeypress == '#'){
        state = States::IDLE;
    }
}

void CustomController::displayFault(Faults fault){
    lcd.pushString("\x0c        ERROR\n--------------------\n");
    
    switch (fault)
    {
    case Faults::DISPENSING_CUP_REMOVED:
        lcd.pushString("Cup removed.");
        break;
    case Faults::DISPENSING_WATER_SHORTAGE:
        lcd.pushString("Water shortage.");
        break;
    case Faults::DISPENSING_SIRUP_SHORTAGE:
        lcd.pushString("Sirup shortage.");
        break;
    case Faults::SELECTION_FLUID_TOO_HIGH:
        lcd.pushString("Input too high.");
        break;
    case Faults::SELECTION_INVALID:
        lcd.pushString("Invalid selection.");
        break;
    default:
        break;
    }

    lcd.pushString("\nPress \'#\' to continue.");

    if(latestKeypress == '#'){
        state = States::IDLE;
        fault = Faults::NONE;
    }
}

void CustomController::heaterOnTemp(int targetTemprature){
    if(cup.readValue()){
        if(temperature.readValue() < targetTemprature - 0.5){
            heater.set(true);
        } else if(temperature.readValue() > targetTemprature + 0.5){
            heater.set(false);
        }
    }else{
        heater.set(false);
    }
}

void CustomController::startWaterPump(void){
    waterPump.set(true);
    waterValve.set(false);
}

void CustomController::startSirupPump(void){
    sirupPump.set(true);
    sirupValve.set(false);
}

bool CustomController::validateCupApperance(void){
    if(cup.readValue()){
        return true;
    }else{
        shutFluids();
        fault = Faults::DISPENSING_CUP_REMOVED;
        return false;
    }
}

void CustomController::shutFluids(void){
    waterPump.set(false);
    waterValve.set(true);
    sirupPump.set(false);
    sirupPump.set(true);
}

void CustomController::updateLeds(void){
    if(waterPump.isOn() == false && waterValve.isOn() == false && sirupPump.isOn() == false && sirupValve.isOn() == false && cup.readValue() == true){
        LedGreen.set(true);
        LedYellow.set(false);
    }else{
        LedGreen.set(false);
        LedYellow.set(true);
    }
}

void CustomController::updateDisplay(void){
    int buffer = (level.readValue() - beginLevelCup) * constants.levelVoltageFactor / (std::stoi(inputTargetLevelWater) + std::stoi(inputTargetLevelSirup)) *100;
    if(buffer <= 100){
        lcd.pushString(buffer + "%");
    }else{
        lcd.pushString("      Done!      ");
    }
}

CustomController::~CustomController()
{
}