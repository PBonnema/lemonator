import Controller
#import exceptions

# Superclass with Constructor and Update function


class Interface():
    class BaseClass():
        def __init__(self):
            pass

        # def update(self) -> None:
        #    raise NotImplementedError("Method update is not implemented")

        # def printDir(self) -> None:
        #    pass

    class Effector(BaseClass):
        def __init__(self):
            pass

        # Sets the Effector state to on
        def switchOn(self) -> None:
            raise NotImplementedError("Method switchOn is not implemented")

        # Sets the Effector state to off

        def switchOff(self) -> None:
            raise NotImplementedError("Method switchOff is not implemented")

        # Returns the Effector state
        def isOn(self) -> bool:
            raise NotImplementedError("Method isOn is not implemented")

    class LED(Effector):
        # Switches between the on and off state
        def toggle(self) -> None:
            raise NotImplementedError("Method toggel is not implemented")

        # Returns the current colour of the led
        def getColour(self) -> bool:
            raise NotImplementedError("Method getColour is not implemented")

    class LCD(Effector):
        # Returns data of the currently on the lcd
        def getLines(self) -> str:
            raise NotImplementedError("Method getlines is not implemented")

        # Sets a string of data on the LCD
        def pushString(self, s: str) -> None:
            raise NotImplementedError("Method pushString is not implemented")

        # Sets 4 lines of white spaces on the lcd
        def clear(self) -> None:
            raise NotImplementedError("Method clear is not implemented")

        # Sets a singel char on the lcd
        def put(self, s: str) -> None:
            raise NotImplementedError("Method put is not implemented")

    class Sensor(BaseClass):
        def __init__(self):
            pass

        # Returns the sensor data
        def readValue(self) -> float:
            raise NotImplementedError("Method readValue is not implemented")

        # Returns the senor data with unit of measurment
        def measure(self) -> str:
            raise NotImplementedError("Method measure is not implemented")

    class PresenceSensor(Sensor):
        # Returns if the cup is presenced
        def readValue(self) -> bool:
            raise NotImplementedError("Method readValue is not implemented")

    class Keypad(Sensor):
        # Sets a singel char in the keypad (keypress controllerulation)
        def push(self, c: chr) -> None:
            raise NotImplementedError("Method push is not implemented")

        # Returns the first char of the Keypad
        def pop(self) -> str:
            raise NotImplementedError("Method pop is not implemented")

        # Pushes a string to the keypad
        def pushString(self, s: str) -> None:
            pass

        # Pops the complete keypad buffer
        def popAll(self) -> str:
            pass

        def readBuffer(self) -> str:
            pass
