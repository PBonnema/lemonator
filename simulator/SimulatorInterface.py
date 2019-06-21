from Interface import Interface

class SimulatorInterface(Interface):
    class Effector(Interface.Effector):
        def __init__(self, object):
            self.object = object

        # Sets the Effector state to on
        def switchOn(self) -> None:
            self.object.switchOn()

        # Sets the Effector state to off
        def switchOff(self) -> None:
            self.object.switchOff()

        # Returns the Effector state
        def isOn(self) -> bool:
            return self.object.isOn()

    class LED(Interface.LED, Effector):
        # Switches between the on and off state
        def toggle(self) -> None:
            self.object.toggle()

    class LEDGreen(Interface.LEDGreen, LED):
        pass

    class LEDYellow(Interface.LEDYellow, LED):
        pass

    class LCD(Interface.LCD, Effector):
        # Sets a string of data on the LCD
        def pushString(self, s: str) -> None:
            self.object.pushString(s)

        # Sets 4 lines of white spaces on the lcd
        def clear(self) -> None:
            self.object.clear()

        # Sets a single char on the lcd
        def putc(self, s: str) -> None:
            self.object.put(s)

    class Sensor(Interface.Sensor):
        def __init__(self, object):
            self.object = object

        #Returns the sensor data
        def readValue(self) -> float:
            return self.object.readValue()

    class PresenceSensor(Interface.PresenceSensor, Sensor):
        # Returns True if the cup is present
        def readValue(self) -> bool:
            return self.object.readValue()

    class Keypad(Interface.Keypad, Sensor):
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
