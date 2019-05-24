from Effector import Effector
from Sensor import Sensor, TemperatureSensor, LevelSensor, ColourSensor, KeyPad
import sys
import copy
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

        Interface = SimulatorInterface        
        control = Interface.Factory(self)

        #Creation of objects 
        #effectors 
        self.PumpA       = control.make(Interface.Effector, 'pumpA')
        self.PumpB       = control.make(Interface.Effector, 'pumpB')
        self.ValveA      = control.make(Interface.Effector, 'valveA')
        self.ValveB      = control.make(Interface.Effector, 'valveB')
        self.Heater      = control.make(Interface.Effector, 'heater')

        #LED's    
        self.LedRedA     = control.make(Interface.LED, 'redA')
        self.LedGreenA   = control.make(Interface.LED, 'greenA')
        self.LedRedB     = control.make(Interface.LED, 'redB')
        self.LedGreenB   = control.make(Interface.LED, 'greenB')
        self.LedGreenM   = control.make(Interface.LED, 'greenM')
        self.LedYellowM  = control.make(Interface.LED, 'yellowM')

        #Sensors
        self.Colour      = control.make(Interface.Sensor, 'colour')
        self.Temperature = control.make(Interface.Sensor, 'temp')
        self.Level       = control.make(Interface.Sensor, 'level')
        self.Cup         = control.make(Interface.PresenceSensor, 'presence')

        #UI
        self.LCDDisplay  = control.make(Interface.LCD, 'lcd')
        #There has to be data in the buffer, before you can write to the buffer(put & pushString)
        self.LCDDisplay.clear()
        self.Keypad      = control.make(Interface.Keypad, 'keypad')


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