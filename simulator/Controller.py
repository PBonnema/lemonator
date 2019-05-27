from Effector import Effector
from Sensor import Sensor, TemperatureSensor, LevelSensor, ColourSensor, KeyPad
import sys
import Constants

from SimulatorInterface import SimulatorInterface

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
    SELECTION_INVALID = 6,
    NONE = 7


class PrettyProgressIcon():
    def __init__(self, stepChange=2):
        #self.icon = '\\'
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

    def __init__(self, sensors, effectors, controlInterface=None):
        self._Controller__sensors = sensors
        self._Controller__effectors = effectors
        self.state = States.IDLE

        if controlInterface == None:
            Interface = SimulatorInterface
        else:
            Interface = controlInterface
        control = Interface.Factory(self)

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
        self.currentLevelWater = 0
        self.currentLevelSyrup = 0
        self.targetLevelSyrupCup = 0
        self.targetLevelWaterCup = 0

        # Clean the keypad just to be sure.
        self.Keypad.popAll()
        self.latestKeypress = None

        self.progress = PrettyProgressIcon()
        self.fault = Faults.NONE

    def update(self) -> None:
        self.latestKeypress = self.Keypad.pop()
        self.LCDDisplay.clear()
        self.updateLeds()

        if self.fault != Faults.NONE:
            self.displayFault(self.fault)

            return

        self.LCDDisplay.pushString(
            "\x0c   Lemonator v1.0\n--------------------\n")

        if self.state == States.IDLE:
            self.idleState()
        elif self.state == States.WAITING_FOR_CUP:
            self.waitingForCupState()
        elif self.state == States.WAITING_USER_SELECTION_ONE:
            self.enterSelectionOneState()
        elif self.state == States.WAITING_USER_SELECTION_TWO:
            self.enterSelectionTwoState()
        elif self.state == States.DISPENSING:
            self.dispensingState()
        elif self.state == States.CALIBRATE:
            self.calibrateState()
        elif self.state == States.DISPLAY_STATS:
            self.displayStatsState()

    def idleState(self) -> None:
        self.LCDDisplay.pushString(
                "A = Start, B = Stats\nC = Calibrate")

        if self.latestKeypress == 'A':
            self.targetLevelWater = ""
            self.targetLevelSyrup = ""

            self.state = States.WAITING_FOR_CUP

        if self.latestKeypress == 'B':
            self.state = States.DISPLAY_STATS

        if self.latestKeypress == 'C':
            self.state = States.CALIBRATE

    def waitingForCupState(self) -> None:
        if self.Cup.readValue():
            print("Cup detected!")
            sys.stdout.flush()
            self.state = States.WAITING_USER_SELECTION_ONE
        else:
            self.LCDDisplay.pushString(
                "Please place a cup\nto continue...\n")

    def enterSelectionOneState(self) -> None:
        self.LCDDisplay.pushString("Water: " + str(self.targetLevelWater))

        if self.latestKeypress.isdigit():
            self.LCDDisplay.putc(self.latestKeypress)
            self.targetLevelWater += self.latestKeypress

        self.LCDDisplay.pushString(" ml (#)\n")

        self.LCDDisplay.pushString(
            "Syrup: " + str(self.targetLevelSyrup) + " ml")

        if self.latestKeypress == '#':
            if not self.targetLevelWater.isnumeric() or int(self.targetLevelWater) <= 0:
                self.fault = Faults.SELECTION_INVALID
                return

            self.targetLevelWaterCup = float(self.targetLevelWater)+3.0
            self.targetLevelWater = float(self.targetLevelWater)

            if self.targetLevelWater > self.liquidLevelWater:
                self.fault = Faults.DISPENSING_WATER_SHORTAGE
            else:
                self.state = States.WAITING_USER_SELECTION_TWO
                self.targetLevelWater /= 100.0

    def enterSelectionTwoState(self) -> None:
        self.LCDDisplay.pushString(
                "Water: " + str(self.targetLevelWater*100.0) + " ml\n")
        self.LCDDisplay.pushString("Syrup: " + str(self.targetLevelSyrup))

        if self.latestKeypress.isdigit():
            self.LCDDisplay.putc(self.latestKeypress)
            self.targetLevelSyrup += self.latestKeypress

        self.LCDDisplay.pushString(" ml (#)")

        if self.latestKeypress == '#':
            if not self.targetLevelSyrup.isnumeric() or int(self.targetLevelSyrup) <= 0:
                self.fault = Faults.SELECTION_INVALID
                return

            self.targetLevelSyrupCup = float(self.targetLevelSyrup)+3.0
            self.targetLevelSyrup = float(self.targetLevelSyrup)

            if self.targetLevelSyrup > self.liquidLevelSyrup:
                self.fault = Faults.DISPENSING_SYRUP_SHORTAGE
            else:
                self.state = States.DISPENSING
    
                self.targetLevelSyrup /= 100.0

    def dispensingState(self) -> None:
        if not self.Cup.readValue():
            self.shutFluid()
            self.fault = Faults.DISPENSING_CUP_REMOVED
            return

        fromTargetPercentage =  int((self.currentLevelSyrup +self.currentLevelWater)/(self.targetLevelWaterCup + self.targetLevelSyrupCup)*100)

        self.LCDDisplay.pushString("     (" + self.progress.get() + ") " + str(fromTargetPercentage) + "%")

        self.setLevel(self.targetLevelWaterCup, self.targetLevelSyrupCup)

        if abs((self.currentLevelSyrup+self.currentLevelWater) - (self.targetLevelWaterCup + self.targetLevelSyrupCup))== 0:
            self.shutFluid()
            self.state = States.IDLE
            self.currentLevelSyrup = 0
            self.currentLevelWater = 0

        self.progress.next()

    def calibrateState(self) -> None:
        #self.liquidLevel1 = Constants.liquidMax
        #self.liquidLevel2 = Constants.liquidMax

        self.LCDDisplay.pushString("Calibration finished!")

        if self.latestKeypress == '#':
            self.state = States.IDLE

    def displayStatsState(self) -> None:
        self.LCDDisplay.pushString(
            str(round(self.liquidLevelWater)) + " ml <|> ")
        self.LCDDisplay.pushString(
            str(round(self.liquidLevelSyrup)) + " ml\n")
        self.LCDDisplay.pushString("Press # to exit.")

        if self.latestKeypress == '#':
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
        elif fault == Faults.SELECTION_INVALID:
            self.LCDDisplay.pushString("Invalid selection.")
        # Keeps the fluid om the given temp

        self.LCDDisplay.pushString("\nPress # to continue.")

        if self.latestKeypress == '#':
            self.state = States.IDLE
            self.fault = Faults.NONE


    def heaterOnTemp(self, targetTemperature: float) -> None:
        currentTemprature = self.Temperature.readValue()
        if currentTemprature < targetTemperature:
            self.Heater.switchOn()
        else:
            self.Heater.switchOff()

    # Keeps the fluid om the given colour
    def setLevel(self, targetLevelSyrup, targetLevelWater) -> None:
        if self.currentLevelSyrup <= targetLevelSyrup:
            self.PumpA.switchOn()
            self.ValveA.switchOff()
            self.currentLevelSyrup += 1
        else:
            self.PumpA.switchOff()
            self.ValveA.switchOn()

        if self.currentLevelWater <= targetLevelWater:
            self.PumpB.switchOn()
            self.ValveB.switchOff()
            self.currentLevelWater += 1
        else:
            self.PumpB.switchOff()
            self.ValveB.switchOn()
        
    

    def shutFluid(self) -> None:
        self.PumpA.switchOff()
        self.PumpB.switchOff()
        self.ValveA.switchOn()
        self.ValveB.switchOn()

    def updateLeds(self) -> None:
        if self.PumpA.isOn() and not self.ValveA.isOn():
            self.LedGreenA.switchOn()
            self.LedRedA.switchOff()
        else:
            self.LedGreenA.switchOff()
            self.LedRedA.switchOn()

        if self.PumpB.isOn() and not self.ValveB.isOn():
            self.LedGreenB.switchOn()
            self.LedRedB.switchOff()
        else:
            self.LedGreenB.switchOff()
            self.LedRedB.switchOn()

        if self.PumpA.isOn() and not self.ValveA.isOn() and self.PumpB.isOn() and not self.ValveB.isOn() and self.Cup.readValue():
            self.LedGreenM.switchOn()
            self.LedYellowM.switchOff()
        else:
            self.LedGreenM.switchOff()
            self.LedYellowM.switchOn()
