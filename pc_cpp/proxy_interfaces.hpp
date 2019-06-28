/** class Effector
{
public:
    bool isOn();
    void set(bool state);
};

class Sensor
{
public:
    int readValue();
};

class LCD : public Effector
{
public:
    void clear();
    void pushString(std::string string);
    void putc(char);
};

class Keypad : public Sensor
{
public:
    char pop();
};

class LED
{
public:
    void set(bool state);
};

class LEDGreen : public LED
{
};
class LEDYellow : public LED
{
};

class HardwareInterface
{
public:
    HardwareInterface(
        int p, ) : lemonator_interface(p_lcd,
                                       p_keypad,
                                       p_distance,
                                       p_color,
                                       p_temperature,
                                       p_reflex,
                                       p_heater,
                                       p_sirup_pump,
                                       p_sirup_valve,
                                       p_water_pump,
                                       p_water_valve,
                                       p_led_green,
                                       p_led_yellow),
                   port(p, log_transactions, log_characters),
                   p_lcd(port),
                   p_keypad(port, "z"),
                   p_distance(port, "d"),
                   p_color(port, "c"),
                   p_temperature(port, "t"),
                   p_reflex(port, "f"),
                   p_heater(port, "h"),
                   p_sirup_pump(port, "sp"),
                   p_sirup_valve(port, "sv"),
                   p_water_pump(port, "wp"),
                   p_water_valve(port, "wv"),
                   p_led_green(port, "g"),
                   p_led_yellow(port, "y")
    {
    }
};
*/