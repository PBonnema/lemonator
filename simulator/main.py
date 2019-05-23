import time

import Simulator
import SimulatorControl

if __name__ == "__main__":
    #Create Simulator instance
    simulator = Simulator.Simulator(False)
    control = SimulatorControl.Factory(simulator)

    #Creation of objects 
    #print(f"Vessel: " + str(vesselObject.getFluidAmount()))
    VesselA = control.make(SimulatorControl.Vessel, 'a')
    VesselB = control.make(SimulatorControl.Vessel, 'b')

    #effectors 
    PumpA       = control.make(SimulatorControl.Effector, 'pumpA')
    PumpB       = control.make(SimulatorControl.Effector, 'pumpB')
    ValveA      = control.make(SimulatorControl.Effector, 'valveA')
    ValveB      = control.make(SimulatorControl.Effector, 'valveB')
    Heater      = control.make(SimulatorControl.Effector, 'heater')

    #LED's    
    LedRedA     = control.make(SimulatorControl.LED, 'redA')
    LedGreenA   = control.make(SimulatorControl.LED, 'greenA')
    LedRedB     = control.make(SimulatorControl.LED, 'redB')
    LedGreenB   = control.make(SimulatorControl.LED, 'greenB')
    LedGreenM   = control.make(SimulatorControl.LED, 'greenM')
    LedYellowM  = control.make(SimulatorControl.LED, 'yellowM')

    #Sensors
    Colour      = control.make(SimulatorControl.Sensor, 'colour')
    Temperature = control.make(SimulatorControl.Sensor, 'temp')
    Level       = control.make(SimulatorControl.Sensor, 'level')
    Cup         = control.make(SimulatorControl.Sensor, 'presence')

    #UI
    LCDDisplay  = control.make(SimulatorControl.LCD, 'lcd')
    #There has to be data in the buffer, before you can write to the buffer(put & pushString)
    LCDDisplay.clear()
    Keypad      = control.make(SimulatorControl.Keypad, 'keypad')

    #A Custom Run function
    def run(debug: bool = True) -> None:
        timestamp = 0
        while True:
            print(timestamp, '----------------------------------------')
            testFunc(timestamp)
            timestamp += 1
            time.sleep(0.05) # update every x seconds
            
            #Update simulator
            simulator._Simulator__plant.update()
            simulator._Simulator__controller.update()
            simulator._Simulator__monitor.update()
            #If debug is True then print state
            if(debug):
                simulator._Simulator__plant.printState()
            
    #Place all code you want to be executed (while the sim runs) here
    def testFunc(timestamp = 0) -> None:
        print(f"Colour:      " + str(Colour.readValue()))
        print(f"Level:       " + str(Level.readValue()))
        print(f"Temperature: " + str(Temperature.readValue()))
        print(f"Cup:         " + str(Cup.readValue()))
        heaterOnTemp(10.0)
        setColourlevel(2.0, 1.0)
        print(getVesselLevel(VesselA, VesselB))

    #Keeps the fluid om the given temp
    def heaterOnTemp(targetTemperature: float) -> None:
        currentTemprature = Temperature.readValue()
        if currentTemprature < targetTemperature:
            Heater.switchOn()
        else:
            Heater.switchOff()

    #Returns the vessels thier levels
    def getVesselLevel(VesselA: SimulatorControl.Vessel, VesselB: SimulatorControl.Vessel):
        return [VesselA.getFluidAmount(), VesselB.getFluidAmount()]

    #Keeps the fluid om the given colour
    def setColourlevel(targetColour: float, targetLevel: float) -> None:
        currentColour = Colour.readValue()
        currentLevel = Level.readValue()
        if currentColour < targetColour:
            if currentLevel <= targetLevel: 
                PumpA.switchOff()
                PumpB.switchOn()
            else:
                shutFluid()
        elif currentColour > targetColour: 
            if currentLevel <= targetLevel:                
                PumpA.switchOn()
                PumpB.switchOff()
            else:
                shutFluid()
        elif currentColour == targetColour:
            if currentLevel <= targetLevel:  
                PumpA.switchOn()
                PumpB.switchOn()
            else:
                shutFluid()

    def shutFluid() -> None:
        PumpA.switchOff()
        PumpB.switchOff()
        ValveA.switchOn()
        ValveB.switchOn()

    def shutValves() -> None:
        ValveA.switchOff()
        ValveB.switchOff()
    
    print("\n==============================================================\n")
    
    PumpA.switchOn()
    PumpB.switchOn()

    Keypad.push('1')
    Keypad.push('2')
    Keypad.push('3')
    Keypad.push('4')
    Keypad.push('5')
    Keypad.push('6')
    Keypad.push('7')
    Keypad.push('8')
    Keypad.push('9')
    Keypad.push('0')
    Keypad.push('a')
    Keypad.push('b')
    Keypad.push('c')
    Keypad.push('d')
    Keypad.push('#')
    Keypad.push('*')

    Keypad.pushString(" - This a string\n")
    for _i in range(16):
       LCDDisplay.put(Keypad.pop())
    print(list(LCDDisplay.getLines()))

    run(False)
