if __name__ == "__main__":

    import Simulator 
    import Effector
    import time
    #Create Simulator instance
    simulator = Simulator.Simulator(False)

    #Superclass with Constructor and Update function
    class BaseClass():       
        def __init__(self):
            self.object = None

        def update(self) -> None:
            self.object.update()

        def printDir(self) -> None:
            print(f"\nObject: " + str(self.object) + "\n")
            for e in dir(self.object):
                if not (e.startswith('__') and e.endswith('__')):
                    print(e)
            print("\n==========================\n")
    
    class Vessel(BaseClass):    
        def __init__(self, objectID : str):
            self.object = simulator._Simulator__plant._vessels[objectID]

        def flowIn(self, amount, colour) -> None:
            self.object.flowIn(amount, colour)

        def heat(self, state: bool):
            self.object.heat()

        def setPresence(self, presence: bool):
            self.object.setPresence(presence)
        
        def getFluidAmount(self) -> int:
            return self.object.getFluidAmount()
        
        def getColour(self) -> float:
            return self.object.getColour()

        def getTemperature(self) -> float:
            return self.object.getTemperature()

        def getPresence(self) -> bool:
            return self.object.getPresence()
        
        def flow(self) -> None:
            return self.object.flow()
            
    class effector(BaseClass):
        def __init__(self, objectID : str):
            self.object = simulator._Simulator__plant._effectors[objectID]

        #Sets the Effector state to on
        def switchOn(self) -> None:
            self.object.switchOn()
        
        #Sets the Effector state to off
        def switchOff(self) -> None:
            self.object.switchOff()

        #Returns the Effector state
        def isOn(self) -> bool:
            return self.object.isOn()

    class LED(effector):
        #Switches between the on and off state
        def toggel(self) -> None:
            self.object.toggel()

        #Returns the current colour of the led
        def getColour(self) -> bool:
            return self.object.getColour()

    class LCD(effector):
        #Returns data of the currently on the lcd
        def getLines(self) -> str:
            return self.object.getLines()
        
        #Sets a string of data on the LCD
        def pushString(self, s: str) -> None:
            self.object.pushString(s)

        #Sets 4 lines of white spaces on the lcd
        def clear(self) -> None:
            self.object.clear()

        #Sets a singel char on the lcd
        def put(self, s: str) -> None:
            self.object.put(s)

    class Sensor(BaseClass):
        def __init__(self, objectID : str):
            self.object = simulator._Simulator__plant._sensors[objectID]

        #Returns the sensor data
        def readValue(self) -> float:
            return self.object.readValue()

        #Returns the senor data with unit of measurment 
        def measure(self) -> str:
            return self.object.measure()

    class PresenceSensor(Sensor):
        #Returns if the cup is presenced
        def readValue(self) -> bool:
            return self.object.readValue()
    
    class Keypad(Sensor):
        #Sets a singel char in the keypad (keypress simulation)
        def push(self, c: chr) -> None:
            self.object.push(c)

        #Returns the first char of the Keypad
        def pop(self) -> str:
            return self.object.pop()

        #Pushes a string to the keypad
        def pushString(self, s: str) -> None:
            for c in s:
                self.object.push(c)
        
        #Pops the complete keypad buffer
        def popAll(self) -> str:
            s = ""
            charBuffer = ''
            while True:
                charBuffer = self.object.pop()
                if charBuffer == '\x00':
                    return s
                s += charBuffer

        def readBuffer(self) -> str:
            s = ""
            charBuffer = ''
            self.push('|')
            while True:
                charBuffer = self.object.pop()
                if charBuffer == '|':
                    return s
                self.object.push(charBuffer)
                s += charBuffer

               
    #Creation of objects 
    #print(f"Vessel: " + str(vesselObject.getFluidAmount()))
    VesselA = Vessel('a')
    VesselB = Vessel('b')

    #effectors 
    PumpA       = effector('pumpA')
    PumpB       = effector('pumpB')
    ValveA      = effector('valveA')
    ValveB      = effector('valveB')
    Heater      = effector('heater')

    #LED's    
    LedRedA     = LED('redA')
    LedGreenA   = LED('greenA')
    LedRedB     = LED('redB')
    LedGreenB   = LED('greenB')
    LedGreenM   = LED('greenM')
    LedYellowM  = LED('yellowM')

    #Sensors
    Colour      = Sensor('colour')
    Temperature = Sensor('temp')
    Level       = Sensor('level')
    Cup         = PresenceSensor('presence')

    #UI
    LCDDisplay  = LCD('lcd')
    #There has to be data in the buffer, before you can write to the buffer(put & pushString)
    LCDDisplay.clear()
    Keypad      = Keypad('keypad')

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
    def heaterOnTemp(targetTemprature: float) -> None:
        currentTemprature = Temperature.readValue()
        if currentTemprature < targetTemprature:
            Heater.switchOn()
        else:
            Heater.switchOff()

    #Returns the vessels thier levels
    def getVesselLevel(VesselA: Vessel, VesselB: Vessel):
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


    