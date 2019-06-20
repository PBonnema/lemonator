from abc import ABC, abstractmethod

class Interface:
    class Effector(ABC):
        # Sets the Effector state to on
        @abstractmethod
        def switchOn(self) -> None:
            raise NotImplementedError("Method switchOn is not implemented")

        # Sets the Effector state to off
        @abstractmethod
        def switchOff(self) -> None:
            raise NotImplementedError("Method switchOff is not implemented")

        # Returns the Effector state
        @abstractmethod
        def isOn(self) -> bool:
            raise NotImplementedError("Method isOn is not implemented")

    class LED(Effector):
        # Switches between the on and off state
        @abstractmethod
        def toggle(self) -> None:
            raise NotImplementedError("Method toggle is not implemented")

    class LEDGreen(LED):
        pass

    class LEDYellow(LED):
        pass

    class LCD(Effector):
        # Sets a string of data on the LCD
        @abstractmethod
        def pushString(self, s: str) -> None:
            raise NotImplementedError("Method pushString is not implemented")

        # Sets 4 lines of white spaces on the lcd
        @abstractmethod
        def clear(self) -> None:
            raise NotImplementedError("Method clear is not implemented")

        # Puts a single char on the lcd
        @abstractmethod
        def putc(self, s: str) -> None:
            raise NotImplementedError("Method put is not implemented")

    class Sensor(ABC):
        # Returns the sensor data
        @abstractmethod
        def readValue(self) -> float:
            raise NotImplementedError("Method readValue is not implemented")

    class PresenceSensor(Sensor):
        # Returns if the cup is present
        @abstractmethod
        def readValue(self) -> bool:
            raise NotImplementedError("Method readValue is not implemented")

    class Keypad(Sensor):
        # Returns the first char of the Keypad
        @abstractmethod
        def pop(self) -> str:
            raise NotImplementedError("Method pop is not implemented")

        # Pops the complete keypad buffer
        @abstractmethod
        def popAll(self) -> str:
            raise NotImplementedError("Method popAll is not implemented")
