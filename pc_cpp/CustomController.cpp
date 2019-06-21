#include "CustomController.hpp"

hwlib::ostream &operator<<(hwlib::ostream &str, const std::string &string)
{
    return str << string.c_str();
}

/** CustomController::CustomController(
    Effector waterPumpObject,
    Effector sirupPumpObject,
    Effector waterValveObject,
    Effector sirupValveObject,
    Effector heaterObject,
    Sensor tempratureObject,
    Sensor levelObject,
    Sensor cupObject,
    LEDGreen LedGreenObject,
    LEDYellow LedYellowObject,
    LCD lcdObject,
    Keypad keypadObject) : waterPump(waterPumpObject), sirupPump(sirupPumpObject), waterValve(waterValveObject), sirupValve(sirupValveObject), heater(heaterObject), temperature(tempratureObject),
                           level(levelObject), LedGreen(LedGreenObject), LedYellow(LedYellowObject), lcd(lcdObject), keypad(keypadObject), proxy(2)**/
CustomController::CustomController() : proxy(2), inputTargetLevelWater("0"), inputTargetLevelSirup("0"), targetHeat("0")
{
    state = States::IDLE;
    fault = Faults::NONE;
    beginLevelCup = 0.0;
    currentLevelCup = beginLevelCup;
    liquidLevelWater = constants.liquidMax;
    liquidLevelSirup = constants.liquidMax;
}

void CustomController::update()
{
    latestKeypress = proxy.p_keypad.getc();

    proxy.p_lcd.putc('\f');

    if (std::stoi(targetHeat) != 0 && state != States::WAITING_USER_HEAT_SELECTION)
    {
        heaterOnTemp(std::stoi(targetHeat));
    }
    if (proxy.p_water_pump.get() || proxy.p_sirup_pump.get())
    {
        if (liquidLevelWater <= 0.0)
        {
            shutFluids();
            fault = Faults::DISPENSING_WATER_SHORTAGE;
        }
        if (liquidLevelSirup <= 0.0)
        {
            shutFluids();
            fault = Faults::DISPENSING_SIRUP_SHORTAGE;
        }
    }

    if (fault != Faults::NONE)
    {
        displayFault(fault);
        return;
    }

    proxy.p_lcd << "\x0c   Lemonator v1.0\n--------------------\n";

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

void CustomController::idleState(void)
{
    proxy.p_lcd << "A = Start, B = Stats\n     C = Heat";

    switch (latestKeypress)
    {
    case 'A':
        inputTargetLevelWater = std::string();
        inputTargetLevelSirup = std::string();
        beginLevelCup = proxy.p_distance.read_mm();
        currentLevelCup = beginLevelCup;
        state = States::WAITING_USER_SELECTION_ONE;
        break;
    case 'B':
        state = States::DISPLAY_STATS;
        break;
    case 'C':
        targetHeat = std::string("0");
        state = States::WAITING_USER_HEAT_SELECTION;
    default:
        //fault = Faults::SELECTION_INVALID;
        break;
    }
}

void CustomController::waitingForCupState(void)
{
    if (proxy.p_reflex.get())
    {
        state = States::WAITING_USER_SELECTION_ONE;
    }
    else
    {
        proxy.p_lcd << "Please place a cup\nto continue...\n";
    }
}

void CustomController::enterSelectionOneState(void)
{
    proxy.p_lcd << "Water: " << inputTargetLevelWater;

    if (isdigit(latestKeypress))
    {
        proxy.p_lcd << latestKeypress;
        inputTargetLevelWater += latestKeypress;
    }

    proxy.p_lcd << "ml (#)\n";
    proxy.p_lcd << "Sirup: " << inputTargetLevelSirup << " ml";

    if (latestKeypress == '#')
    {
        if (std::stoi(inputTargetLevelWater) < 0)
        {
            fault = Faults::SELECTION_INVALID;
        }

        if (std::stoi(inputTargetLevelWater) > liquidLevelWater)
        {
            fault = Faults::DISPENSING_WATER_SHORTAGE;
        }
        else
        {
            state = States::WAITING_USER_SELECTION_TWO;
        }
    }
}

void CustomController::enterSelectionTwoState(void)
{
    proxy.p_lcd << "Water: " << inputTargetLevelWater << " ml\n";
    proxy.p_lcd << "Sirup: " << inputTargetLevelSirup << " ml\n";

    if (isdigit(latestKeypress))
    {
        proxy.p_lcd.putc(latestKeypress);
        inputTargetLevelSirup += latestKeypress;
    }

    proxy.p_lcd << "ml (#)";

    if (latestKeypress == '#')
    {
        if (std::stoi(inputTargetLevelSirup) < 0)
        {
            fault = Faults::DISPENSING_SIRUP_SHORTAGE;
        }

        if (std::stoi(inputTargetLevelSirup) > liquidLevelSirup)
        {
            fault = Faults::DISPENSING_SIRUP_SHORTAGE;
        }
        else
        {
            state = States::DISPENSING_WATER;
        }
    }
}

void CustomController::enterheatSelectionState(void)
{
    proxy.p_lcd << "Heat: " << targetHeat;

    if (isdigit(latestKeypress))
    {
        proxy.p_lcd.putc(latestKeypress);
        targetHeat += latestKeypress;
    }

    std::cout << targetHeat << std::flush;

    proxy.p_lcd << " °C (#)";

    if (latestKeypress == '#')
    {
        if (std::stoi(targetHeat) < 0)
        {
            fault = Faults::SELECTION_INVALID;
        }
        else if (std::stoi(targetHeat) >= 100)
        {
            fault = Faults::SELECTION_TEMP_TOO_HIGH;
        }
        else
        {
            state = States::IDLE;
        }
    }
}

void CustomController::dispensingWaterState(void)
{
    if (validateCupApperance())
    {
        startWaterPump();
        updateDisplay();

        if (((proxy.p_distance.read_mm() - currentLevelCup) * constants.levelVoltageFactor) - std::stoi(inputTargetLevelWater) >= 0)
        {
            shutFluids();
            currentLevelCup = proxy.p_distance.read_mm();
            liquidLevelWater -= std::stoi(inputTargetLevelWater);
            state = States::DISPENSING_SIRUP;
        }
    }
}

void CustomController::dispensingSirupState(void)
{
    if (validateCupApperance())
    {
        startSirupPump();
        updateDisplay();

        if (((proxy.p_distance.read_mm() - currentLevelCup) * constants.levelVoltageFactor) - std::stoi(inputTargetLevelSirup) >= 0)
        {
            shutFluids();
            currentLevelCup = proxy.p_distance.read_mm();
            liquidLevelSirup -= std::stoi(inputTargetLevelSirup);
            state = States::IDLE;
        }
    }
}

void CustomController::displayStatsState(void)
{
    proxy.p_lcd << (std::to_string(liquidLevelWater).c_str()) << "ml <|> ";
    proxy.p_lcd << (std::to_string(liquidLevelSirup).c_str()) << "ml\n";
    proxy.p_lcd << "Press \'#\' to exit.";

    if (latestKeypress == '#')
    {
        state = States::IDLE;
    }
}

void CustomController::displayFault(Faults fault)
{
    proxy.p_lcd << "\x0c        ERROR\n--------------------\n";

    switch (fault)
    {
    case Faults::DISPENSING_CUP_REMOVED:
        proxy.p_lcd << "Cup removed.";
        break;
    case Faults::DISPENSING_WATER_SHORTAGE:
        proxy.p_lcd << "Water shortage.";
        break;
    case Faults::DISPENSING_SIRUP_SHORTAGE:
        proxy.p_lcd << "Sirup shortage.";
        break;
    case Faults::SELECTION_FLUID_TOO_HIGH:
        proxy.p_lcd << "Input too high.";
        break;
    case Faults::SELECTION_INVALID:
        proxy.p_lcd << "Invalid selection.";
        break;
    default:
        break;
    }

    proxy.p_lcd << "\nPress \'#\' to continue.";

    if (latestKeypress == '#')
    {
        state = States::IDLE;
        fault = Faults::NONE;
    }
}

void CustomController::heaterOnTemp(int targetTemprature)
{
    if (proxy.p_reflex.get())
    {
        if (proxy.p_temperature.read_mc() < targetTemprature - 0.5)
        {
            //heater.set(true);
            proxy.p_heater.set(true);
        }
        else if (proxy.p_temperature.read_mc() > targetTemprature + 0.5)
        {
            //heater.set(false);
            proxy.p_heater.set(false);
        }
    }
    else
    {
        //heater.set(false);
        proxy.p_heater.set(false);
    }
}

void CustomController::startWaterPump(void)
{
    //waterPump.set(true);
    //waterValve.set(false);

    proxy.p_water_pump.set(true);
    proxy.p_water_valve.set(false);
}

void CustomController::startSirupPump(void)
{
    //sirupPump.set(true);
    //sirupValve.set(false);

    proxy.p_sirup_pump.set(true);
    proxy.p_sirup_valve.set(false);
}

bool CustomController::validateCupApperance(void)
{
    if (proxy.p_reflex.get())
    {
        return true;
    }
    else
    {
        shutFluids();
        fault = Faults::DISPENSING_CUP_REMOVED;
        return false;
    }
}

void CustomController::shutFluids(void)
{
    /**waterPump.set(false);
    waterValve.set(true);
    sirupPump.set(false);
    sirupValve.set(true);**/

    proxy.p_water_pump.set(false);
    proxy.p_water_valve.set(true);
    proxy.p_sirup_pump.set(false);
    proxy.p_sirup_valve.set(true);
}

void CustomController::updateLeds(void)
{
    if (proxy.p_water_pump.get() == false && proxy.p_water_valve.get() == false && proxy.p_sirup_pump.get() == false && proxy.p_sirup_valve.get() == false && proxy.p_reflex.get() == true)
    {
        //LedGreen.set(true);
        //LedYellow.set(false);
        proxy.p_led_green.set(true);
        proxy.p_led_yellow.set(false);
    }
    else
    {
        //LedGreen.set(false);
        //LedYellow.set(true);
        proxy.p_led_green.set(false);
        proxy.p_led_yellow.set(true);
    }
}

void CustomController::updateDisplay(void)
{
    int buffer = (proxy.p_distance.read_mm() - beginLevelCup) * constants.levelVoltageFactor / (std::stoi(inputTargetLevelWater) + std::stoi(inputTargetLevelSirup)) * 100;
    if (buffer <= 100)
    {
        //lcd.pushString(buffer + "%");
        proxy.p_lcd << buffer << '%';
    }
    else
    {
        //lcd.pushString("      Done!      ");
        proxy.p_lcd << "      Done!      ";
    }
}

CustomController::~CustomController()
{
}