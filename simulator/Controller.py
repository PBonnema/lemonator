from Effector import Effector
from Sensor import Sensor, TemperatureSensor, LevelSensor, ColourSensor, KeyPad
import sys

import SimulatorInterface

from enum import Enum

class States(Enum):
    IDLE = 0,
    WAITING_FOR_USER_ACTION = 1,
    WAITING_CUP_PLACEMENT = 2,
    WAITING_USER_SELECTION = 3,
    DISPENSING = 4,
    DISPENSING_DONE = 5,
    FAULT = 6


class Controller:

    def __init__(self, sensors, effectors):
        """Controller is build using two Dictionaries:
        - sensors: Dict[str, Sensor], using strings 'temp', 'color', 'level'
        - effectors: Dict[str, Effector], using strings 'heater', 'pumpA', 'pumpB'
        """
        self._Controller__sensors = sensors
        self._Controller__effectors = effectors
        self.state = States.IDLE

        
        control = SimulatorInterface.Factory(self)

        #Creation of objects 
        #effectors 
        self.PumpA       = control.make(SimulatorInterface.Effector, 'pumpA')
        self.PumpB       = control.make(SimulatorInterface.Effector, 'pumpB')
        self.ValveA      = control.make(SimulatorInterface.Effector, 'valveA')
        self.ValveB      = control.make(SimulatorInterface.Effector, 'valveB')
        self.Heater      = control.make(SimulatorInterface.Effector, 'heater')

        #LED's    
        self.LedRedA     = control.make(SimulatorInterface.LED, 'redA')
        self.LedGreenA   = control.make(SimulatorInterface.LED, 'greenA')
        self.LedRedB     = control.make(SimulatorInterface.LED, 'redB')
        self.LedGreenB   = control.make(SimulatorInterface.LED, 'greenB')
        self.LedGreenM   = control.make(SimulatorInterface.LED, 'greenM')
        self.LedYellowM  = control.make(SimulatorInterface.LED, 'yellowM')

        #Sensors
        self.Colour      = control.make(SimulatorInterface.Sensor, 'colour')
        self.Temperature = control.make(SimulatorInterface.Sensor, 'temp')
        self.Level       = control.make(SimulatorInterface.Sensor, 'level')
        self.Cup         = control.make(SimulatorInterface.Sensor, 'presence')

        #UI
        self.LCDDisplay  = control.make(SimulatorInterface.LCD, 'lcd')
        #There has to be data in the buffer, before you can write to the buffer(put & pushString)
        self.LCDDisplay.clear()
        self.Keypad      = control.make(SimulatorInterface.Keypad, 'keypad')


    def update(self) -> None:
        #Runs the test func 
        #self.testFunc()
        keypressed = self._Controller__sensors['keypad'].pop()

        if self.state == States.IDLE:
            self._Controller__effectors['lcd'].clear()
            self._Controller__effectors['lcd'].pushString("\t0000 Lemonator\n Please press the A\n button to continue...\n")

            if keypressed == 'A':
                sys.stdout.flush()
                self.state = States.WAITING_FOR_USER_ACTION

        if self.state == States.WAITING_FOR_USER_ACTION:
            self._Controller__effectors['lcd'].clear()
            self._Controller__effectors['lcd'].pushString("\t0000 Please place a cup.\n")


    def testFunc(self, timestamp = 0) -> None:
        print(f"Colour:      " + str(self.Colour.readValue()))
        print(f"Level:       " + str(self.Level.readValue()))
        print(f"Temperature: " + str(self.Temperature.readValue()))
        print(f"Cup:         " + str(self.Cup.readValue()))
        self.heaterOnTemp(10.0)
        self.setColourlevel(2.0, 1.0)

    #Keeps the fluid om the given temp
    def heaterOnTemp(self, targetTemperature: float) -> None:
        currentTemprature = self.Temperature.readValue()
        if currentTemprature < targetTemperature:
            self.Heater.switchOn()
        else:
            self.Heater.switchOff()

    #Keeps the fluid om the given colour
    def setColourlevel(self, targetColour: float, targetLevel: float) -> None:
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

    def shutValves(self) -> None:
        self.ValveA.switchOff()
        self.ValveB.switchOff()