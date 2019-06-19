import CustomController as Controller
import time
from Interface import Interface
import lemonator
import sys

# Superclass with Constructor and Update function

lm = None


class HardwareInterface(Interface):
    class BaseClass():
        def __init__(self):
            global lm

            # Ugly singleton.
            if not lm:
                print("Creating COM port connection...")
                sys.stdout.flush()
                lm = lemonator.lemonator(1)
            #self.lm = lm

            #self.object = object
            #self.controller = controller

    class Effector(BaseClass):
        def __init__(self):
            super().__init__()
            # super().__init__(
            #    controller._Controller__effectors[objectID], controller)

            # Sets the Effector state to on
        def switchOn(self) -> None:
            pass

        # Sets the Effector state to off
        def switchOff(self) -> None:
            pass

        # Returns the Effector state
        def isOn(self) -> bool:
            pass

    class LED(Effector):
        def __init__(self):
            super().__init__()

        # Switches between the on and off state
        def toggle(self) -> None:
            pass

        # Returns the current colour of the led
        def getColour(self) -> bool:
            pass

    class LCD(Effector):
        def __init__(self):
            super().__init__()

            global lm

            self.lm = lm

        # Returns data of the currently on the lcd
        def getLines(self) -> str:
            pass

        # Sets a string of data on the LCD
        def pushString(self, s: str) -> None:
            pass

        # Sets 4 lines of white spaces on the lcd
        def clear(self) -> None:
            pass

        # Sets a single char on the lcd
        def putc(self, s: str) -> None:
            self.lm.lcd.putc(s[0])

    class Sensor(BaseClass):
        def __init__(self):
            super().__init__()

            global lm

            self.lm = lm
            # super().__init__(
            #    controller._Controller__sensors[objectID], controller)
            self.buffer = []

        # Returns the sensor data
        def readValue(self) -> float:
            pass
            # return self.object.readValue()

        def setValue(self, value) -> None:
            #self.object._value = value
            pass

        # Returns the sensor data with unit of measurement
        def measure(self) -> str:
            # return self.object.measure()
            pass

        def getAverage(self, numberOfReads) -> float:
            # if len(self.buffer) != 0:
            #     numberOfReads = min(len(self.buffer), numberOfReads)
            #     return sum(self.buffer[-numberOfReads:]) / numberOfReads
            # raise ValueError("Sensor buffer is empty")
            pass

    class PresenceSensor(Sensor):
        # Returns if the cup is presenced
        def readValue(self) -> bool:
            # return self.object.readValue()
            pass

        def set(self, state: bool) -> None:
            #self.object._value = state
            pass

    class Keypad(Sensor):
        def __init__(self):
            super().__init__()

            self.keypad = self.lm.keypad

        # Returns the first char of the Keypad
        def pop(self) -> str:
            # return 'A'
            # return self.object.pop()
            return self.keypad.getc()

        # Pops the complete keypad buffer
        def popAll(self) -> str:
            s = ''
            charBuffer = ''
            while True:
                charBuffer = self.pop()
                if charBuffer == '\x00':
                    return s
                s += charBuffer

    class Factory:
        def make(self, instType, *instArgs):
            if not issubclass(instType, HardwareInterface.BaseClass):
                raise TypeError(
                    f"Class instance {instType.__name__} does not have a valid base class.")

            inst = instType(*instArgs)

            return inst
