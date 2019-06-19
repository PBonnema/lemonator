import CustomController as Controller
import time
from Interface import Interface

class SimulatorInterface(Interface):
    class BaseClass():
        def __init__(self, object, controller: Controller):
            self.object = object
            self.controller = controller

    class Effector(BaseClass):
        def __init__(self, controller: Controller, objectID: str):
            super().__init__(
                controller._Controller__effectors[objectID], controller)

        # Sets the Effector state to on
        def switchOn(self) -> None:
            self.object.switchOn()

        # Sets the Effector state to off
        def switchOff(self) -> None:
            self.object.switchOff()

        # Returns the Effector state
        def isOn(self) -> bool:
            return self.object.isOn()

    class LED(Effector):
        # Switches between the on and off state
        def toggle(self) -> None:
            self.object.toggle()

    class LCD(Effector):
        # Sets a string of data on the LCD
        def pushString(self, s: str) -> None:
            self.object.pushString(s)

        # Sets 4 lines of white spaces on the lcd
        def clear(self) -> None:
            self.object.clear()

        # Sets a single char on the lcd
        def putc(self, s: str) -> None:
            self.object.put(s)

    class Sensor(BaseClass):
        def __init__(self, controller: Controller, objectID: str):
            super().__init__(
                controller._Controller__sensors[objectID], controller)
            self.buffer = []

        # Returns the sensor data
        def readValue(self) -> float:
            return self.object.readValue()

    class PresenceSensor(Sensor):
        # Returns if the cup is presenced
        def readValue(self) -> bool:
            return self.object.readValue()

    class Keypad(Sensor):
        # Returns the first char of the Keypad
        def pop(self) -> str:
            return self.object.pop()

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
        def __init__(self, controller: Controller):
            self.Controller = controller

        def make(self, instType, *instArgs):
            if not issubclass(instType, SimulatorInterface.BaseClass):
                raise TypeError(
                    f"Class instance {instType.__name__} does not have a valid base class.")

            inst = instType(self.Controller, *instArgs)

            return inst
