from Effector import Effector
from Sensor import Sensor, TemperatureSensor, LevelSensor, ColourSensor, KeyPad
import sys
import Constants

# from SimulatorInterface import SimulatorInterface

from enum import Enum


class States(Enum):
    IDLE = 0,
    WAITING_FOR_CUP = 1,
    WAITING_USER_SELECTION_ONE = 3,
    DISPENSING = 4,
    DISPENSING_DONE = 5,
    DISPENSING_FAULT = 6,
    CALIBRATE = 7,
    DISPLAY_STATS = 8,
    WAITING_USER_SELECTION_TWO = 9,
    WAITING_USER_HEAT_SELECTION = 10


class Faults(Enum):
    DISPENSING_CUP_REMOVED = 0,
    DISPENSING_CUP_OVERFLOW = 1,
    DISPENSING_WATER_SHORTAGE = 2,
    DISPENSING_SYRUP_SHORTAGE = 3,
    SELECTION_TEMP_TOO_HIGH = 4
    SELECTION_FLUID_TOO_HIGH = 5,
    SELECTION_INVALID = 6,
    NONE = 7


class PrettyProgressIcon():
    def __init__(self, stepChange=2):
        self.icons = ['\\', '|', '/', '-']
        self.updateStep = stepChange
        self.stepChange = stepChange
        self.iconStep = 0

    def next(self):
        self.updateStep += 1

        if self.updateStep < self.stepChange:
            return

        self.iconStep += 1

        if self.iconStep == len(self.icons):
            self.iconStep = 0

        self.currentStep = 0

    def get(self):
        return self.icons[self.iconStep]


class Controller:

    def __init__(self, sensors, effectors, Interface):
        self._Controller__sensors = sensors
        self._Controller__effectors = effectors

        self.state = States.IDLE

        control = Interface.Factory(self)

        # effectors
        self.pumpA = control.make(Interface.Effector, 'pumpA')
        self.pumpB = control.make(Interface.Effector, 'pumpB')
        self.valveA = control.make(Interface.Effector, 'valveA')
        self.valveB = control.make(Interface.Effector, 'valveB')
        self.heater = control.make(Interface.Effector, 'heater')

        # LED's
        self.ledRedA = control.make(Interface.LED, 'redA')
        self.ledGreenA = control.make(Interface.LED, 'greenA')
        self.ledRedB = control.make(Interface.LED, 'redB')
        self.ledGreenB = control.make(Interface.LED, 'greenB')
        self.ledGreenM = control.make(Interface.LED, 'greenM')
        self.ledYellowM = control.make(Interface.LED, 'yellowM')

        # Sensors
        self.colour = control.make(Interface.Sensor, 'colour')
        self.temperature = control.make(Interface.Sensor, 'temp')
        self.level = control.make(Interface.Sensor, 'level')
        self.cup = control.make(Interface.PresenceSensor, 'presence')

        # UI
        self.lcd = control.make(Interface.LCD, 'lcd')
        # There has to be data in the buffer, before you can write to the buffer(put & pushString)
        self.lcd.clear()
        self.keypad = control.make(Interface.Keypad, 'keypad')

        # @mike What is the function of this array?
        self.objects = [self.pumpA, self.pumpB, self.valveA, self.valveB, self.heater, self.ledRedA, self.ledGreenA, self.ledRedB,
                        self.ledGreenB, self.ledGreenM, self.ledYellowM, self.colour, self.temperature, self.level, self.cup, self.lcd, self.keypad]

        self.targetLevelWater = ""
        self.targetLevelSyrup = ""
        self.liquidLevelWater = Constants.liquidMax
        self.liquidLevelSyrup = Constants.liquidMax
        self.currentLevelWater = 0
        self.currentLevelSyrup = 0
        self.targetLevelSyrupCup = 0
        self.targetLevelWaterCup = 0

        # Clean the keypad just to be sure.
        self.keypad.popAll()
        self.latestKeypress = None

        self.progress = PrettyProgressIcon()
        self.fault = Faults.NONE
        self.targetHeat = ""

    def update(self) -> None:
        for i in self.objects:
            i.update()

        self.latestKeypress = self.keypad.pop()
        self.lcd.clear()
        self.updateLeds()

        if self.targetHeat != "" and self.state != States.WAITING_USER_HEAT_SELECTION:
            self.heaterOnTemp(float(self.targetHeat) / 20.0)

        if self.fault != Faults.NONE:
            self.displayFault(self.fault)
            return

        self.lcd.pushString(
            "\x0c   Lemonator v1.0\n--------------------\n")

        if self.state == States.IDLE:
            self.idleState()
        elif self.state == States.WAITING_FOR_CUP:
            self.waitingForCupState()
        elif self.state == States.WAITING_USER_SELECTION_ONE:
            self.enterSelectionOneState()
        elif self.state == States.WAITING_USER_SELECTION_TWO:
            self.enterSelectionTwoState()
        elif self.state == States.WAITING_USER_HEAT_SELECTION:
            self.enterHeatSelectionState()
        elif self.state == States.DISPENSING:
            self.dispensingState()
        elif self.state == States.CALIBRATE:
            self.calibrateState()
        elif self.state == States.DISPLAY_STATS:
            self.displayStatsState()

    def idleState(self) -> None:
        self.lcd.pushString(
            "A = Start, B = Stats\nC = Calibrate, D = Heat")

        if self.latestKeypress == 'A':
            self.targetLevelWater = ""
            self.targetLevelSyrup = ""

            self.state = States.WAITING_FOR_CUP

        if self.latestKeypress == 'B':
            self.state = States.DISPLAY_STATS

        if self.latestKeypress == 'C':
            self.state = States.CALIBRATE

        if self.latestKeypress == 'D':
            self.targetHeat = ""
            self.state = States.WAITING_USER_HEAT_SELECTION

    def waitingForCupState(self) -> None:
        if self.cup.readValue():
            print("Cup detected!")
            sys.stdout.flush()
            self.state = States.WAITING_USER_SELECTION_ONE
        else:
            self.lcd.pushString(
                "Please place a cup\nto continue...\n")

    def enterSelectionOneState(self) -> None:
        self.lcd.pushString("Water: " + str(self.targetLevelWater))

        if self.latestKeypress.isdigit():
            self.lcd.putc(self.latestKeypress)
            self.targetLevelWater += self.latestKeypress

        self.lcd.pushString(" ml (#)\n")

        self.lcd.pushString(
            "Syrup: " + str(self.targetLevelSyrup) + " ml")

        if self.latestKeypress == '#':
            if not self.targetLevelWater.isnumeric() or int(self.targetLevelWater) <= 0:
                self.fault = Faults.SELECTION_INVALID
                return

            self.targetLevelWaterCup = self.setCupValue(
                float(self.targetLevelWater))
            self.targetLevelWater = float(self.targetLevelWater)

            if self.targetLevelWater > self.liquidLevelWater:
                self.fault = Faults.DISPENSING_WATER_SHORTAGE
            else:
                self.state = States.WAITING_USER_SELECTION_TWO
                self.targetLevelWater /= 100.0

    def enterSelectionTwoState(self) -> None:
        self.lcd.pushString(
            "Water: " + str(self.targetLevelWater*100.0) + " ml\n")
        self.lcd.pushString("Syrup: " + str(self.targetLevelSyrup))

        if self.latestKeypress.isdigit():
            self.lcd.putc(self.latestKeypress)
            self.targetLevelSyrup += self.latestKeypress

        self.lcd.pushString(" ml (#)")

        if self.latestKeypress == '#':
            if not self.targetLevelSyrup.isnumeric() or int(self.targetLevelSyrup) <= 0:
                self.fault = Faults.SELECTION_INVALID
                return

            self.targetLevelSyrupCup = self.setCupValue(
                float(self.targetLevelSyrup))
            self.targetLevelSyrup = float(self.targetLevelSyrup)

            if self.targetLevelSyrup > self.liquidLevelSyrup:
                self.fault = Faults.DISPENSING_SYRUP_SHORTAGE
            else:
                self.state = States.DISPENSING

                self.targetLevelSyrup /= 100.0

    def enterHeatSelectionState(self) -> None:
        self.lcd.pushString("Heat: " + str(self.targetHeat))

        if self.latestKeypress.isdigit():
            self.lcd.putc(self.latestKeypress)
            self.targetHeat += self.latestKeypress

        self.lcd.pushString(" C (#)")

        if self.latestKeypress == '#':
            if not self.targetHeat.isnumeric() or int(self.targetHeat) <= 0 or int(self.targetHeat) >= 100:
                self.fault = Faults.SELECTION_INVALID
                return

            self.targetHeat = float(self.targetHeat)
            self.state = States.IDLE

    def dispensingState(self) -> None:
        if not self.cup.readValue():
            self.shutFluid()
            self.fault = Faults.DISPENSING_CUP_REMOVED
            return

        self.setLevel(self.targetLevelWaterCup, self.targetLevelSyrupCup)

        self.LCDDisplay.pushString(f"     (" + self.progress.get() + ") " + "{:.1}".format(str(
            (self.currentLevelSyrup + self.currentLevelWater)/(self.targetLevelWaterCup + self.targetLevelSyrupCup)*100)) + "%")

        print(f"Theoretical: " + str(self.currentLevelSyrup+self.currentLevelWater) +
              " |  Readvalue: " + str(self.Level.readValue()))
        sys.stdout.flush()

        if (self.currentLevelWater - self.targetLevelWaterCup) == 0 and (self.currentLevelSyrup - self.targetLevelSyrupCup) == 0:
            self.shutFluid()
            self.state = States.IDLE
            self.currentLevelSyrup = 0
            self.currentLevelWater = 0

        self.progress.next()

    def calibrateState(self) -> None:
        # self.liquidLevel1 = Constants.liquidMax
        # self.liquidLevel2 = Constants.liquidMax

        self.lcd.pushString("Calibration finished!")

        if self.latestKeypress == '#':
            self.state = States.IDLE

    def displayStatsState(self) -> None:
        self.lcd.pushString(
            str(round(self.liquidLevelWater)) + " ml <|> ")
        self.lcd.pushString(
            str(round(self.liquidLevelSyrup)) + " ml\n")
        self.lcd.pushString("Press # to exit.")

        if self.latestKeypress == '#':
            self.state = States.IDLE

    def displayFault(self, fault: Faults) -> None:
        self.lcd.pushString("\x0c        ERROR\n--------------------\n")

        if fault == Faults.DISPENSING_CUP_REMOVED:
            self.lcd.pushString("Cup removed.")
        elif fault == Faults.DISPENSING_WATER_SHORTAGE:
            self.lcd.pushString("Water shortage.")
        elif fault == Faults.DISPENSING_SYRUP_SHORTAGE:
            self.lcd.pushString("Syrup shortage.")
        elif fault == Faults.SELECTION_TEMP_TOO_HIGH:
            self.lcd.pushString("Temperature too high.")
        elif fault == Faults.SELECTION_INVALID:
            self.lcd.pushString("Invalid selection.")
        # Keeps the fluid om the given temp

        self.lcd.pushString("\nPress # to continue.")

        if self.latestKeypress == '#':
            self.state = States.IDLE
            self.fault = Faults.NONE

    def heaterOnTemp(self, targetTemperature: float) -> None:
        currentTemprature = self.temperature.getAverage(3)
        if currentTemprature < targetTemperature:
            self.heater.switchOn()
        else:
            self.heater.switchOff()

    # Keeps the fluid om the given colour
    def setLevel(self, targetLevelWater, targetLevelSyrup) -> None:
        if self.currentLevelWater < targetLevelWater:
            self.pumpA.switchOn()
            self.valveA.switchOff()
            self.currentLevelWater += 1
        else:
            self.pumpA.switchOff()
            self.valveA.switchOn()

        if self.currentLevelSyrup < targetLevelSyrup:
            self.pumpB.switchOn()
            self.valveB.switchOff()
            self.currentLevelSyrup += 1
        else:
            self.pumpB.switchOff()
            self.valveB.switchOn()

    def shutFluid(self) -> None:
        self.pumpA.switchOff()
        self.pumpB.switchOff()
        self.valveA.switchOn()
        self.valveB.switchOn()

    def updateLeds(self) -> None:
        if self.pumpA.isOn() and not self.valveA.isOn():
            self.ledGreenA.switchOn()
            self.ledRedA.switchOff()
        else:
            self.ledGreenA.switchOff()
            self.ledRedA.switchOn()

        if self.pumpB.isOn() and not self.valveB.isOn():
            self.ledGreenB.switchOn()
            self.ledRedB.switchOff()
        else:
            self.ledGreenB.switchOff()
            self.ledRedB.switchOn()

        if self.pumpA.isOn() and not self.valveA.isOn() and self.pumpB.isOn() and not self.valveB.isOn() and self.cup.readValue():
            self.ledGreenM.switchOff()
            self.ledYellowM.switchOn()
        else:
            self.ledGreenM.switchOn()
            self.ledYellowM.switchOff()

    def setCupValue(self, value: float) -> float:
        return value + value / (value/3.0)
