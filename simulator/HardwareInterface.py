from Interface import Interface
import lemonator

class HardwareInterface(Interface):
    class Effector(Interface.Effector):
        # Sets the Effector state to on
        def switchOn(self) -> None:
            pass

        # Sets the Effector state to off
        def switchOff(self) -> None:
            pass

        # Returns the Effector state
        def isOn(self) -> bool:
            pass

    class Heater(Effector):
        # Sets the Effector state to on
        def switchOn(self) -> None:
            pass

        # Sets the Effector state to off
        def switchOff(self) -> None:
            pass

        # Returns the Effector state
        def isOn(self) -> bool:
            pass

    class Valve(Effector):
        def __init__(self, type : str):
            self.type = type

        # Sets the Effector state to on
        def switchOn(self) -> None:
            pass

        # Sets the Effector state to off
        def switchOff(self) -> None:
            pass

        # Returns the Effector state
        def isOn(self) -> bool:
            pass

    class Pump(Effector):
        def __init__(self, type : str):
            self.type = type

        # Sets the Effector state to on
        def switchOn(self) -> None:
            pass

        # Sets the Effector state to off
        def switchOff(self) -> None:
            pass

        # Returns the Effector state
        def isOn(self) -> bool:
            pass

    class LED(Interface.LED, Effector):
        # Switches between the on and off state
        def toggle(self) -> None:
            pass

    class LEDGreen(Interface.LEDGreen, LED):
        pass

    class LEDYellow(Interface.LEDYellow, LED):
        pass

    class LCD(Interface.LCD, Effector):
        # Sets a string of data on the LCD
        def pushString(self, s: str) -> None:
            pass

        # Sets 4 lines of white spaces on the lcd
        def clear(self) -> None:
            pass

        # Sets a single char on the lcd
        def putc(self, s: str) -> None:
            pass

    class Sensor(Interface.Sensor):
        # Returns the sensor data
        def readValue(self) -> float:
            pass
            # return self.object.readValue()

    class LevelSensor(Interface.Sensor):
        def readValue(self):
            pass

    class TemperatureSensor(Interface.Sensor):
        def readValue(self):
            pass

    class ColourSensor(Interface.Sensor):
        def readValue(self):
            pass

    class PresenceSensor(Sensor):
        # Returns if the cup is presenced
        def readValue(self) -> bool:
            # return self.object.readValue()
            pass

    class Keypad(Sensor):
        # Returns the first char of the Keypad
        def pop(self) -> str:
            # return 'A'
            # return self.object.pop()
            pass
        # Pops the complete keypad buffer
        def popAll(self) -> str:
            # s = ''
            # charBuffer = ''
            # while True:
            #     charBuffer = self.pop()
            #     if charBuffer == '\x00':
            #         return s
            #     s += charBuffer
            pass
