from Effector import Effector
from Sensor import Sensor, TemperatureSensor, LevelSensor, ColourSensor, KeyPad
import sys
import Constants
from enum import Enum


class States(Enum):
    IDLE = 0,
    WAITING_FOR_CUP = 1,
    WAITING_USER_SELECTION_ONE = 3,
    DISPENSING_WATER = 4,
    DISPENSING_SYRUP = 5,
    DISPENSING_DONE = 6,
    DISPENSING_FAULT = 7,
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


# This class is used to display a progress spinner during pumping
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
        # Assign sensors and effectors to the controller
        self._Controller__sensors = sensors
        self._Controller__effectors = effectors

        # Set initial state value
        self.state = States.IDLE

        # Set initial fault to flase/none 
        self.fault = Faults.NONE

        # Create control object
        control = Interface.Factory(self)
        
        # Create effector objects
        self.pumpA = control.make(Interface.Effector, 'pumpA')
        self.pumpB = control.make(Interface.Effector, 'pumpB')
        self.valveA = control.make(Interface.Effector, 'valveA')
        self.valveB = control.make(Interface.Effector, 'valveB')
        self.heater = control.make(Interface.Effector, 'heater')

        # Create LED's objects
        self.ledRedA = control.make(Interface.LED, 'redA')
        self.ledGreenA = control.make(Interface.LED, 'greenA')
        self.ledRedB = control.make(Interface.LED, 'redB')
        self.ledGreenB = control.make(Interface.LED, 'greenB')
        self.ledGreenM = control.make(Interface.LED, 'greenM')
        self.ledYellowM = control.make(Interface.LED, 'yellowM')

        # Create sensors objects
        self.colour = control.make(Interface.Sensor, 'colour')
        self.temperature = control.make(Interface.Sensor, 'temp')
        self.level = control.make(Interface.Sensor, 'level')
        self.cup = control.make(Interface.PresenceSensor, 'presence')

        # Create UI objects
        self.lcd = control.make(Interface.LCD, 'lcd')
        self.lcd.clear() # There has to be data in the buffer, before you can write to the buffer(put & pushString)
        
        self.keypad = control.make(Interface.Keypad, 'keypad')

        # Array for update function calls so that during the run all objects will be updated
        self.objects = [self.colour, self.temperature, self.level, self.lcd, self.keypad, self.pumpA, self.pumpB, self.valveA, self.valveB, self.ledRedA, self.ledRedB, self.ledGreenA, self.ledGreenB, self.ledGreenM, self.ledYellowM]

        # Set default values
        self.inputTargetLevelWater = ""
        self.inputTargetLevelSyrup = ""
        self.beginLevelCup = self.level.readValue()   
        self.currentLevelCup = self.level.readValue()
        self.liquidLevelWater = Constants.liquidMax
        self.liquidLevelSyrup = Constants.liquidMax
        self.targetHeat = ""

        # Clean the keypad just to be sure.
        self.keypad.popAll()
        self.latestKeypress = None

        # Set progress
        self.progress = PrettyProgressIcon()
        
    

    def update(self) -> None:
        # Update all objects to represent the current simulator state.
        for i in self.objects:
            i.update()

        self.latestKeypress = self.keypad.pop()

        # Clear visuals.
        self.lcd.clear()
        self.updateLeds()

        # Check if the heater matches the target temperature.
        if self.targetHeat != "" and self.state != States.WAITING_USER_HEAT_SELECTION:
            self.heaterOnTemp(float(self.targetHeat) / 20.0)

        # If the pumps are flowing, validate that there is still enough liquid left. We don't want to be running dry.
        if self.pumpB.isOn() or self.pumpA.isOn():
            if int(self.liquidLevelSyrup) <= 0:
                self.shutFluid()
                self.fault = Faults.DISPENSING_SYRUP_SHORTAGE
            if int(self.liquidLevelWater) <= 0:
                self.shutFluid()
                self.flault = Faults.DISPENSING_WATER_SHORTAGE

        # If a fault is set, we display the fault to the user. We bypass the statemachine to make sure nothing dangerous will happen.
        if self.fault != Faults.NONE:
            self.displayFault(self.fault)
            return

        self.lcd.pushString(
            "\x0c   Lemonator v1.0\n--------------------\n")

        # Part of the state machine; state handling.
        if self.state == States.IDLE:
            # Switch to idle state. The machine is ready to receive various actions.
            self.idleState()
        elif self.state == States.WAITING_FOR_CUP:
            # Someone decided to take a drink, we want to make sure that a cup is present.
            self.waitingForCupState()
        elif self.state == States.WAITING_USER_SELECTION_ONE:
            # User should select the amount of water.
            self.enterSelectionOneState()
        elif self.state == States.WAITING_USER_SELECTION_TWO:
            # User should select the amount of syrup.
            self.enterSelectionTwoState()
        elif self.state == States.WAITING_USER_HEAT_SELECTION:
            # User should select the target heat.
            self.enterHeatSelectionState()
        elif self.state == States.DISPENSING_WATER:
            # The machine is dispensing water.
            self.dispensingWaterState()
        elif self.state == States.DISPENSING_SYRUP:
            # The machine is dispensing syrup.
            self.dispensingSyrupState()
        elif self.state == States.DISPLAY_STATS:
            # We display the machine statistics to the user.
            self.displayStatsState()

    def idleState(self) -> None:
        self.lcd.pushString(
            "A = Start, B = Stats\n     D = Heat")
        
        if self.latestKeypress == 'A':
            self.inputTargetLevelWater = ""
            self.inputTargetLevelSyrup = ""
            self.beginLevelCup = self.level.readValue()   
            self.currentLevelCup = self.level.readValue()

            self.state = States.WAITING_FOR_CUP

        if self.latestKeypress == 'B':
            self.state = States.DISPLAY_STATS

        if self.latestKeypress == 'D':
            self.targetHeat = ""
            self.state = States.WAITING_USER_HEAT_SELECTION

    def waitingForCupState(self) -> None:
        if self.cup.readValue():
            self.state = States.WAITING_USER_SELECTION_ONE
        else:
            self.lcd.pushString(
                "Please place a cup\nto continue...\n")

    # This function gets userinput for the amount of water.
    def enterSelectionOneState(self) -> None:
        self.lcd.pushString("Water: " + str(self.inputTargetLevelWater))

        if self.latestKeypress.isdigit():
            self.lcd.putc(self.latestKeypress)
            self.inputTargetLevelWater += self.latestKeypress

        self.lcd.pushString(" ml (#)\n")

        self.lcd.pushString(
            "Syrup: " + str(self.inputTargetLevelSyrup) + " ml")

        if self.latestKeypress == '#':
            if not self.inputTargetLevelWater.isnumeric() or int(self.inputTargetLevelWater) <= 0:
                self.fault = Faults.SELECTION_INVALID
                return
           
            self.inputTargetLevelWater = float(self.inputTargetLevelWater)            

            if self.inputTargetLevelWater > self.liquidLevelWater:
                self.fault = Faults.DISPENSING_WATER_SHORTAGE
            else:
                self.state = States.WAITING_USER_SELECTION_TWO
    
    # This function gets userinput for the amount of syrup.
    def enterSelectionTwoState(self) -> None:
        self.lcd.pushString(
            "Water: " + str(int(self.inputTargetLevelWater)) + " ml\n")
        self.lcd.pushString("Syrup: " + str(self.inputTargetLevelSyrup))

        if self.latestKeypress.isdigit():
            self.lcd.putc(self.latestKeypress)
            self.inputTargetLevelSyrup += self.latestKeypress

        self.lcd.pushString(" ml (#)")

        if self.latestKeypress == '#':
            if not self.inputTargetLevelSyrup.isnumeric() or int(self.inputTargetLevelSyrup) <= 0:
                self.fault = Faults.SELECTION_INVALID
                return
            self.inputTargetLevelSyrup = float(self.inputTargetLevelSyrup)

            if float(self.inputTargetLevelSyrup) > self.liquidLevelSyrup:
                self.fault = Faults.DISPENSING_SYRUP_SHORTAGE
            else:
                self.state = States.DISPENSING_WATER
                self.beginLevelCup = self.level.readValue()

    # This function gets userinput for the heater (in celsius)
    def enterHeatSelectionState(self) -> None:
        self.lcd.pushString(f"Heat: {self.targetHeat}")

        if self.latestKeypress.isdigit():
            self.lcd.putc(self.latestKeypress)
            self.targetHeat += self.latestKeypress

        self.lcd.pushString(" °C (#)")

        if self.latestKeypress == '#':
            if not self.targetHeat.isnumeric() or int(self.targetHeat) <= 0 or int(self.targetHeat) >= 100:
                self.fault = Faults.SELECTION_INVALID
                return

            self.targetHeat = float(self.targetHeat)
            self.state = States.IDLE

    # This function will dispence the given amount of water
    def dispensingWaterState(self) -> None:
        # Check if the cup is stil present.
        if not self.validateCupAppearance():
            return

        self.startWaterPump()
        self.updateDisplay()

        self.test = ((self.level.readValue()- self.currentLevelCup) * Constants.levelVoltageFactor)

        if (((self.level.readValue()- self.currentLevelCup) * Constants.levelVoltageFactor) >= self.inputTargetLevelWater):
            self.shutFluid()
            self.currentLevelCup = self.level.readValue()
            self.liquidLevelWater -= float(self.inputTargetLevelWater)
            self.state = States.DISPENSING_SYRUP

        self.progress.next()


    # This function will dispence the given amount of syrup
    def dispensingSyrupState(self) -> None:
        # Check if the cup is stil present.
        if not self.validateCupAppearance():
            return

        self.startSyrupPump()
        self.updateDisplay()

        if (((self.level.readValue() - self.currentLevelCup)*Constants.levelVoltageFactor) - self.inputTargetLevelSyrup) >= 0:
            self.shutFluid()
            self.beginLevelCup = self.level.readValue()
            self.liquidLevelSyrup -= float(self.inputTargetLevelSyrup)
            self.state = States.IDLE
            
        self.progress.next()

    # This function will display stats of the vessels on the LCD
    def displayStatsState(self) -> None:
        self.lcd.pushString(f"{round(self.liquidLevelWater)} ml <|> ")
        self.lcd.pushString(f"{round(self.liquidLevelSyrup)} ml\n")
        self.lcd.pushString("Press # to exit.")

        if self.latestKeypress == '#':
            self.state = States.IDLE

    # Displays the error message corresponding to a given fault state
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
    
    # Will keep the liquid on a given temprature
    def heaterOnTemp(self, targetTemperature: float) -> None:
        currentTemprature = self.temperature.getAverage(3)
        if self.cup.readValue():
            if currentTemprature < targetTemperature:
                self.heater.switchOn()
            else:
                self.heater.switchOff()
        else:
            self.heater.switchOff()

    #Checks if the pumps and valves are correctly set, if not it will correct them.
    def startWaterPump(self, onlyOneCanBeOn = True) -> None:
        if not self.pumpA.isOn():
            self.pumpA.switchOn()
        if not self.valveA.isOn():
            self.valveA.switchOff()
        if onlyOneCanBeOn:
            if self.pumpB.isOn():
                self.pumpB.switchOff()
            if self.valveB.isOn():
                self.valveB.switchOn()

    #Checks if the pump and valves are correctly set, if not it will correct them.
    def startSyrupPump(self, onlyOneCanBeOn = True) -> None:  
        if not self.pumpB.isOn():
            self.pumpB.switchOn()
        if not self.valveB.isOn():
            self.valveB.switchOff()
        if onlyOneCanBeOn:
            if self.pumpA.isOn():
                self.pumpA.switchOff()
            if self.valveA.isOn():
                self.valveA.switchOn()

    # Checks if the cup is pressent
    def validateCupAppearance(self) -> bool:
        if not self.cup.readValue():
            self.shutFluid()
            self.fault = Faults.DISPENSING_CUP_REMOVED
            return False
        return True
         
    # Stops the pumps and opens valves to stop the liquid form flowing.
    # Only effects pumps that are on to prevent unnecessary calls to the pumps and valves.
    def shutFluid(self) -> None:
        if self.pumpA.isOn():
            self.pumpA.switchOff()
            self.valveA.switchOn()
        if self.pumpB.isOn():
            self.pumpB.switchOff()
            self.valveB.switchOn()

    # This function checks the states of effectors and turns led on/off accordingly.
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
    
    # Updates the progress procentage and displays its new value on the display.\
    def updateDisplay(self) -> None:
        progress = round(((self.level.readValue()-self.beginLevelCup)*Constants.levelVoltageFactor/(self.inputTargetLevelWater+self.inputTargetLevelSyrup))*100.0)
        if progress <= 100:
            self.lcd.pushString(f"     (" + self.progress.get() + ") " + str(progress) + "%")
        else:
            self.lcd.pushString(f"      Done!      ")