from Effector import Effector
from Sensor import Sensor, TemperatureSensor, LevelSensor, ColourSensor, KeyPad
import sys
import copy
import SimulatorInterface


class Controller:

    def __init__(self, sensors, effectors, controlInterface = None):
        self._Controller__sensors = sensors
        self._Controller__effectors = effectors

        if controlInterface == None:
            Interface = SimulatorInterface.SimulatorInterface
        else:
            Interface = controlInterface
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

        self.LedM = False


    def update(self) -> None:
        #Runs the test func
        self.testFunc()


    def testFunc(self, timestamp = 0) -> None:
        print(f"Colour:      " + str(self.Colour.readValue()))
        print(f"Level:       " + str(self.Level.readValue()))
        print(f"Temperature: " + str(self.Temperature.readValue()))
        print(f"Cup:         " + str(self.Cup.readValue()))
        self.heaterOnTemp(10.0)
        self.setColourlevel(2.0, 1.0)
        self.updateLeds()

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