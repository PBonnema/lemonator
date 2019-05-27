from Effector import Effector
from Sensor import Sensor, TemperatureSensor, LevelSensor, ColourSensor, KeyPad
import sys
import Constants

import SimulatorInterface

from enum import Enum


class States(Enum):
    IDLE = 0,
    WAITING_FOR_CUP = 1,
    WAITING_CUP_PLACEMENT = 2,
    WAITING_USER_SELECTION_ONE = 3,
    DISPENSING = 4,
    DISPENSING_DONE = 5,
    DISPENSING_FAULT = 6,
    CALIBRATE = 7,
    DISPLAY_STATS = 8,
    WAITING_USER_SELECTION_TWO = 9,
    FAULT_OCCURED = 10


class Faults(Enum):
    DISPENSING_CUP_REMOVED = 0,
    DISPENSING_CUP_OVERFLOW = 1,
    DISPENSING_WATER_SHORTAGE = 2,
    DISPENSING_SYRUP_SHORTAGE = 3,
    SELECTION_TEMP_TOO_HIGH = 4
    SELECTION_FLUID_TOO_HIGH = 5,
    NONE = 6


class PrettyProgressIcon():
    def __init__(self, stepChange=2):
        self.icon = '\\'
        self.currentStep = stepChange
        self.stepChange = stepChange

    def next(self):
        self.currentStep += 1

        if self.currentStep < self.stepChange:
            return

        self.currentStep = 0

        if self.icon == '\\':
            self.icon = '|'
        elif self.icon == '|':
            self.icon = '/'
        elif self.icon == '/':
            self.icon = '-'
        elif self.icon == '-':
            self.icon = '\\'

    def get(self):
        return self.icon


class Controller:

    def __init__(self, sensors, effectors, controlInterface=None):
        self._Controller__sensors = sensors
        self._Controller__effectors = effectors
        self.state = States.IDLE

        control = SimulatorInterface.Factory(self)

        # Creation of objects
        # effectors
        self.PumpA = control.make(SimulatorInterface.Effector, 'pumpA')
        self.PumpB = control.make(SimulatorInterface.Effector, 'pumpB')
        self.ValveA = control.make(SimulatorInterface.Effector, 'valveA')
        self.ValveB = control.make(SimulatorInterface.Effector, 'valveB')
        self.Heater = control.make(SimulatorInterface.Effector, 'heater')

        if controlInterface == None:
            Interface = SimulatorInterface
        else:
            Interface = controlInterface
        control = Interface.Factory(self)

        # Creation of objects
        # effectors
        self.PumpA = control.make(Interface.Effector, 'pumpA')
        self.PumpB = control.make(Interface.Effector, 'pumpB')
        self.ValveA = control.make(Interface.Effector, 'valveA')
        self.ValveB = control.make(Interface.Effector, 'valveB')
        self.Heater = control.make(Interface.Effector, 'heater')

        # LED's
        self.LedRedA = control.make(Interface.LED, 'redA')
        self.LedGreenA = control.make(Interface.LED, 'greenA')
        self.LedRedB = control.make(Interface.LED, 'redB')
        self.LedGreenB = control.make(Interface.LED, 'greenB')
        self.LedGreenM = control.make(Interface.LED, 'greenM')
        self.LedYellowM = control.make(Interface.LED, 'yellowM')

        # Sensors
        self.Colour = control.make(Interface.Sensor, 'colour')
        self.Temperature = control.make(Interface.Sensor, 'temp')
        self.Level = control.make(Interface.Sensor, 'level')
        self.Cup = control.make(Interface.PresenceSensor, 'presence')

        # UI
        self.LCDDisplay = control.make(Interface.LCD, 'lcd')
        # There has to be data in the buffer, before you can write to the buffer(put & pushString)
        self.LCDDisplay.clear()
        self.Keypad = control.make(SimulatorInterface.Keypad, 'keypad')

        self.targetLevelWater = ""
        self.targetLevelSyrup = ""
        self.liquidLevelWater = Constants.liquidMax
        self.liquidLevelSyrup = Constants.liquidMax

        # Clean the keypad just to be sure.
        self.Keypad.popAll()

        self.progress = PrettyProgressIcon()
        self.fault = Faults.NONE

    def update(self) -> None:
        keypressed = self.Keypad.pop()
        self.LCDDisplay.clear()

        if self.fault != Faults.NONE:
            self.displayFault(self.fault)

            if keypressed == '#':
                self.state = States.IDLE
                self.fault = Faults.NONE

            return

        self.LCDDisplay.pushString(
            "\x0c   Lemonator v1.0\n--------------------\n")

        if self.state == States.IDLE:
            self.LCDDisplay.pushString(
                "A = Start, B = Stats\nC = Calibrate")

            if keypressed == 'A':
                self.targetLevelWater = ""
                self.targetLevelSyrup = ""

                self.state = States.WAITING_FOR_CUP

            if keypressed == 'B':
                self.state = States.DISPLAY_STATS

            if keypressed == 'C':
                self.state = States.CALIBRATE

        elif self.state == States.WAITING_FOR_CUP:
            if self.Cup.readValue():
                print("Cup detected!")
                sys.stdout.flush()
                self.state = States.WAITING_USER_SELECTION_ONE
            else:
                self.LCDDisplay.pushString(
                    "Please place a cup\nto continue...\n")

        elif self.state == States.WAITING_USER_SELECTION_ONE:
            self.LCDDisplay.pushString("Water: " + str(self.targetLevelWater))

            if keypressed.isdigit():
                self.LCDDisplay.putc(keypressed)
                self.targetLevelWater += keypressed

            self.LCDDisplay.pushString(" ml (#)\n")

            self.LCDDisplay.pushString(
                "Syrup: " + str(self.targetLevelSyrup) + " ml")

            if keypressed == '#':

                self.targetLevelWater = float(self.targetLevelWater)

                if self.targetLevelWater > self.liquidLevelWater:
                    self.fault = Faults.DISPENSING_WATER_SHORTAGE
                else:
                    self.state = States.WAITING_USER_SELECTION_TWO
                    self.targetLevelWater /= 100.0

        elif self.state == States.WAITING_USER_SELECTION_TWO:
            self.LCDDisplay.pushString(
                "Water: " + str(self.targetLevelWater) + " ml\n")
            self.LCDDisplay.pushString("Syrup: " + str(self.targetLevelSyrup))

            if keypressed.isdigit():
                self.LCDDisplay.putc(keypressed)
                self.targetLevelSyrup += keypressed

            self.LCDDisplay.pushString(" ml (#)")

            if keypressed == '#':
                self.targetLevelSyrup = float(self.targetLevelSyrup)

                if self.targetLevelSyrup > self.liquidLevelSyrup:
                    self.fault = Faults.DISPENSING_SYRUP_SHORTAGE
                else:
                    self.state = States.DISPENSING
                    self.targetLevelSyrup /= 100.0

        elif self.state == States.DISPENSING:
            if not self.Cup.readValue():
                self.shutFluid()
                self.fault = Faults.DISPENSING_CUP_REMOVED
                return

            fromTargetPercentage = int(
                (self.Level.readValue() * 100.0) / self.targetLevelWater)

            self.LCDDisplay.pushString(
                "     (" + self.progress.get() + ") " + str(fromTargetPercentage) + "%")

            self.setColourlevel(self.targetLevelWater)

            if abs(self.Level.readValue() - self.targetLevelWater) < 0.01 or self.Level.readValue() > self.targetLevelWater:
                self.shutFluid()
                self.state = States.IDLE

            self.progress.next()

        elif self.state == States.CALIBRATE:
            #self.liquidLevel1 = Constants.liquidMax
            #self.liquidLevel2 = Constants.liquidMax

            self.LCDDisplay.pushString("Calibration finished!")

            if keypressed == '#':
                self.state = States.IDLE

        elif self.state == States.DISPLAY_STATS:
            self.LCDDisplay.pushString(
                str(round(self.liquidLevelWater)) + " ml <|> ")
            self.LCDDisplay.pushString(
                str(round(self.liquidLevelSyrup)) + " ml\n")
            self.LCDDisplay.pushString("Press # to exit.")

            if keypressed == '#':
                self.state = States.IDLE

    def displayFault(self, fault: Faults) -> None:
        self.LCDDisplay.pushString("\x0c        ERROR\n--------------------\n")

        if fault == Faults.DISPENSING_CUP_REMOVED:
            self.LCDDisplay.pushString("Cup removed.")
        elif fault == Faults.DISPENSING_WATER_SHORTAGE:
            self.LCDDisplay.pushString("Water shortage.")
        elif fault == Faults.DISPENSING_SYRUP_SHORTAGE:
            self.LCDDisplay.pushString("Syrup shortage.")
        elif fault == Faults.SELECTION_TEMP_TOO_HIGH:
            self.LCDDisplay.pushString("Temperature too high.")
        # Keeps the fluid om the given temp

        self.LCDDisplay.pushString("\nPress # to continue.")

    def heaterOnTemp(self, targetTemperature: float) -> None:
        currentTemprature = self.Temperature.readValue()
        if currentTemprature < targetTemperature:
            self.Heater.switchOn()
        else:
            self.Heater.switchOff()

    # Keeps the fluid om the given colour
    def setColourlevel(self, targetLevel=100,  targetColour=1.65) -> None:
        currentColour = self.Colour.readValue()
        currentLevel = self.Level.readValue()
        if currentColour < targetColour:
            if currentLevel <= targetLevel:
                self.PumpA.switchOff()
                self.PumpB.switchOn()
            else:
                self.shutFluid()
        elif currentColour > targetColour:
            if currentLevel <= targetLevel:
                self.PumpA.switchOn()
                self.PumpB.switchOff()
            else:
                self.shutFluid()
        elif currentColour == targetColour:
            if currentLevel <= targetLevel:
                self.PumpA.switchOn()
                self.PumpB.switchOn()
            else:
                self.shutFluid()

    def shutFluid(self) -> None:
        self.PumpA.switchOff()
        self.PumpB.switchOff()
        self.ValveA.switchOn()
        self.ValveB.switchOn()

    def cupPresence(self) -> None:
        if not self.Cup.readValue():
            self.shutFluid()

    def reset(self) -> None:
        self.PumpA.switchOff()
        self.PumpB.switchOff()
        self.ValveA.switchOff()
        self.ValveB.switchOff()
        self.Heater.switchOff()

    def updateLeds(self) -> None:
        if self.PumpA.isOn() == True and self.ValveA.isOn() == False:
            self.LedGreenA.switchOn()
            self.LedRedA.switchOff()
        else:
            self.LedGreenA.switchOff()
            self.LedRedA.switchOn()

        if self.PumpB.isOn() == True and self.ValveB.isOn() == False:
            self.LedGreenB.switchOn()
            self.LedRedB.switchOff()
        else:
            self.LedGreenB.switchOff()
            self.LedRedB.switchOn()

        if self.PumpA.isOn() == True and self.ValveA.isOn() == False and self.PumpB.isOn() == True and self.ValveB.isOn() == False and self.Cup.readValue() == True:
            self.LedGreenM.switchOn()
            self.LedYellowM.switchOff()
        else:
            self.LedGreenM.switchOff()
            self.LedYellowM.switchOn()
