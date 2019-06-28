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

    //*this.putc('\f');

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
        flushLCD();
        return;
    }

    writeLCD("\x0c   Lemonator v1.0\n--------------------\n");

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
        break;
    default:
        break;
    };

    flushLCD();
}

void CustomController::idleState(void)
{
    writeLCD("A = Start, B = Stats\n     C = Heat");

    switch (latestKeypress)
    {
    case 'A':
        inputTargetLevelWater = std::string("0");
        inputTargetLevelSirup = std::string("0");
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
        break;
    default:
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
        writeLCD("Please place a cup\nto continue...\n");
    }
}

void CustomController::enterSelectionOneState(void)
{

    if (isdigit(latestKeypress))
    {
        inputTargetLevelWater += latestKeypress;
    }

    writeLCD("Water: " + inputTargetLevelWater);

    writeLCD(" ml (#)\n");
    writeLCD("Sirup: " + inputTargetLevelSirup + " ml");

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
    if (isdigit(latestKeypress))
    {
        inputTargetLevelSirup += latestKeypress;
    }

    writeLCD("Water: " + inputTargetLevelWater + " ml\n");
    writeLCD("Sirup: " + inputTargetLevelSirup + " ml\n");

    writeLCD(" ml (#)");

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
    if (isdigit(latestKeypress))
    {
        targetHeat += latestKeypress;
    }

    writeLCD("Heat: " + targetHeat + " C (#)");
    writeLCD("\n");

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
            flushLCD();
            writeLCD('\f');
            Sleep(20);
        }
    }
}

void CustomController::dispensingWaterState(void)
{
    if (validateCupApperance())
    {
        startWaterPump();
        updateDisplay();
        flushLCD();

        //if (((proxy.p_distance.read_mm() - currentLevelCup) * constants.levelVoltageFactor) - std::stoi(inputTargetLevelWater) >= 0)
        //{
        Sleep(250 * std::stoi(inputTargetLevelWater));
        shutFluids();
        currentLevelCup = proxy.p_distance.read_mm();
        liquidLevelWater -= std::stoi(inputTargetLevelWater);
        state = States::DISPENSING_SIRUP;
        //}
    }
}

void CustomController::dispensingSirupState(void)
{
    if (validateCupApperance())
    {
        startSirupPump();
        updateDisplay();
        flushLCD();

        //if (((proxy.p_distance.read_mm() - currentLevelCup) * constants.levelVoltageFactor) - std::stoi(inputTargetLevelSirup) >= 0)
        //{
        Sleep(250 * std::stoi(inputTargetLevelSirup));
        shutFluids();
        currentLevelCup = proxy.p_distance.read_mm();
        liquidLevelSirup -= std::stoi(inputTargetLevelSirup);
        state = States::IDLE;
        //}
    }
}

void CustomController::displayStatsState(void)
{
    writeLCD((std::to_string(static_cast<int>(liquidLevelWater)).c_str()));
    writeLCD("ml <|> ");
    writeLCD((std::to_string(static_cast<int>(liquidLevelSirup)).c_str()));
    writeLCD("ml\n");
    writeLCD("Press \'#\' to exit.");

    if (latestKeypress == '#')
    {
        state = States::IDLE;
    }
}

void CustomController::displayFault(Faults &fault)
{
    writeLCD("\x0c        ERROR\n--------------------\n");

    switch (fault)
    {
    case Faults::DISPENSING_CUP_REMOVED:
        writeLCD("Cup removed.");
        break;
    case Faults::DISPENSING_WATER_SHORTAGE:
        writeLCD("Water shortage.");
        break;
    case Faults::DISPENSING_SIRUP_SHORTAGE:
        writeLCD("Sirup shortage.");
        break;
    case Faults::SELECTION_FLUID_TOO_HIGH:
        writeLCD("Input too high.");
        break;
    case Faults::SELECTION_INVALID:
        writeLCD("Invalid selection.");
        break;
    default:
        break;
    }

    writeLCD("\nPress \'#\' to continue.");

    if (latestKeypress == '#')
    {
        state = States::IDLE;
        fault = Faults::NONE;
    }
}

void CustomController::heaterOnTemp(int targetTemperature)
{
    float heaterTemp = readHeaterTemp();

    //std::cout << "Heater target temperature: " << targetTemperature << std::endl;
    //std::cout << "Current temperature: " << heaterTemp << std::endl;

    if (validateCupApperance())
    {
        if (heaterTemp < targetTemperature - 0.5)
        {
            //heater.set(true);
            proxy.p_heater.set(true);
        }
        else if (heaterTemp > targetTemperature + 0.5)
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

        // Cup sensor is broken, we need to return always true.
        //shutFluids();
        //fault = Faults::DISPENSING_CUP_REMOVED;
        //return false;

        return true;
    }
}

float CustomController::readHeaterTemp(void)
{
    return proxy.p_temperature.read_mc() / 1000.0;
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
    if (proxy.p_water_pump.get())
    {
        writeLCD("Dispensing water...");
    }
    else if (proxy.p_sirup_pump.get())
    {
        writeLCD("Dispensing sirup...");
    }
    else
    {
        writeLCD("Heating up...");
    }
}

void CustomController::writeLCD(const std::string &s)
{
    if (lcdBufferOld.size() >= (lcdBufferNew.size() + s.size()))
    {
        if (s.compare(lcdBufferOld.substr(lcdBufferNew.size(), s.size())) == 0)
        {
            mayLCDRefresh = false;
        }
        else
        {
            mayLCDRefresh = true;
        }
    }

    lcdBufferNew += s;

    //std::cout << "old: " << lcdBufferOld << std::endl;
    //std::cout << "new: " << lcdBufferNew << std::endl;
}

void CustomController::writeLCD(const char ch)
{
    std::cout << "Char: " << ch << std::endl
              << std::flush;
    writeLCD(std::to_string(ch));
}

void CustomController::flushLCD(bool force)
{
    if (force || mayLCDRefresh)
    {
        Sleep(10);
        proxy.p_lcd << '\f';
        Sleep(10);
        proxy.p_lcd << lcdBufferNew;
    }

    lcdBufferOld = lcdBufferNew;
    lcdBufferNew.clear();
}

CustomController::~CustomController()
{
}