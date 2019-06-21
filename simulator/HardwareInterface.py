from Interface import Interface
import lemonator
import time

class HardwareInterface(Interface):
    class Effector(Interface.Effector):
        # Sets the Effector state to on
        def switchOn(self) -> None:
            pass

        # Sets the Effector state to off
        def switchOff(self) -> None:
            pass

    class Heater(Effector):
        def __init__(self, hw):
            self.hw = hw

        # Sets the Effector state to on
        def switchOn(self) -> None:
            time.sleep(0.05)
            print("Turning on heater...")
            self.hw.heater.set(True)

        # Sets the Effector state to off
        def switchOff(self) -> None:
            time.sleep(0.05)
            print("Turning off heater...")
            self.hw.heater.set(False)

        # Returns the Effector state
        def isOn(self) -> bool:
            print("Heater is")
            time.sleep(0.05)
            print(self.hw.heater.get())
            time.sleep(0.05)
            return self.hw.heater.get()

    class Valve(Effector):
        def __init__(self, hw, type : str):
            self.hw = hw
            self.type = type

        # Sets the Effector state to on
        def switchOn(self) -> None:
            if self.type == 'A':
                time.sleep(0.05)
                self.hw.water_valve.set(True)
            elif self.type == 'B':
                time.sleep(0.05)
                self.hw.sirup_valve.set(True)

        # Sets the Effector state to off
        def switchOff(self) -> None:
            if self.type == 'A':
                time.sleep(0.05)
                self.hw.water_valve.set(False)
            elif self.type == 'B':
                time.sleep(0.05)
                self.hw.sirup_valve.set(False)

        # Returns the Effector state
        def isOn(self) -> bool:
            if self.type == 'A':
                return self.hw.water_valve.get()
            elif self.type == 'B':
                return self.hw.sirup_valve.get()

    class Pump(Effector):
        def __init__(self, hw, type : str):
            self.hw = hw
            self.type = type

        # Sets the Effector state to on
        def switchOn(self) -> None:
            if self.type == 'A':
                time.sleep(0.05)
                self.hw.water_pump.set(True)
            elif self.type == 'B':
                time.sleep(0.05)
                self.hw.sirup_pump.set(True)

        # Sets the Effector state to off
        def switchOff(self) -> None:
            if self.type == 'A':
                time.sleep(0.05)
                self.hw.water_pump.set(False)
            elif self.type == 'B':
                time.sleep(0.05)
                self.hw.sirup_pump.set(False)

        # Returns the Effector state
        def isOn(self) -> bool:
            if self.type == 'A':
                return self.hw.water_pump.get()
            elif self.type == 'B':
                return self.hw.sirup_pump.get()

    class LED(Interface.LED, Effector):
        # Switches between the on and off state
        def toggle(self) -> None:
            pass

        def isOn(self) -> None:
            pass

    class LEDGreen(Interface.LEDGreen, LED):
        def __init__(self, hw):
            self.hw = hw

        def switchOn(self) -> None:
            time.sleep(0.05)
            self.hw.led_green.set(True)

        def switchOff(self) -> None:
            time.sleep(0.05)
            self.hw.led_green.set(False)


    class LEDYellow(Interface.LEDYellow, LED):
        def __init__(self, hw):
            self.hw = hw

        def switchOn(self) -> None:
            time.sleep(0.05)
            self.hw.led_yellow.set(True)

        def switchOff(self) -> None:
            time.sleep(0.05)
            self.hw.led_yellow.set(False)

    class LCD(Interface.LCD, Effector):
        def __init__(self, hw):
            self.hw = hw

        # Sets a string of data on the LCD
        def pushString(self, s: str) -> None:
            for ch in s:
                self.putc(ch)

        # Sets 4 lines of white spaces on the lcd
        def clear(self) -> None:
            self.putc('\f')

        # Sets a single char on the lcd
        def putc(self, s: str) -> None:
            
            if not s:
                return

            if len(s) > 0:
                self.hw.lcd.putc(s[0])

        # Returns the Effector state
        def isOn(self) -> bool:
            return True


    class Sensor(Interface.Sensor):
        # Returns the sensor data
        def readValue(self) -> float:
            return 0
            # return self.object.readValue()

    class LevelSensor(Interface.Sensor):
        def __init__(self, hw):
            self.hw = hw

        def readValue(self) -> float:
            #time.sleep(0.05)
            val = float(self.hw.distance.read_mm()) * 4.28
            print("Distance: " + str(val))
            return 0

    class TemperatureSensor(Interface.Sensor):
        def __init__(self, hw):
            self.hw = hw

        def readValue(self) -> float:
            time.sleep(0.05)
            temp = float(int(self.hw.temperature.read_mc()) / 1000.0)
            print(temp)
            return temp
    class ColourSensor(Interface.Sensor):
        def __init__(self, hw):
            self.hw = hw

        def readValue(self):
            pass

    class PresenceSensor(Sensor):
        def __init__(self, hw):
            self.hw = hw

        # Returns if the cup is presenced
        def readValue(self) -> bool:
            time.sleep(0.05)
            return True
            #return self.hw.reflex.get()

    class Keypad(Sensor):
        def __init__(self, hw):
            self.hw = hw

        # Returns the first char of the Keypad
        def pop(self) -> str:
            time.sleep(0.05)
            return str(self.hw.keypad.getc())
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
