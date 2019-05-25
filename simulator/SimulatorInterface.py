import Controller
import time

#Superclass with Constructor and Update function
class BaseClass():      
    def __init__(self, controller : Controller):
        self.object = None
        self.Controller = controller
        #self.Controller = controller

    def update(self) -> None:
        self.object.update()

    def printDir(self) -> None:
        print(f"\nObject: " + str(object) + "\n")
        for e in dir(self.object):
            if not (e.startswith('__') and e.endswith('__')):
                print(e)
        print("\n==========================\n")
            
'''
class Vessel(BaseClass): 
    def __init__(self, controller : Controller, objectID : str):
        super(Vessel, self).__init__(controller)
        self.object = self.Controller._Controller__plant._vessels[objectID]
        
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
'''
        
class Effector(BaseClass):
    def __init__(self, controller : Controller, objectID : str):
        super(Effector, self).__init__(controller)

        self.object = self.Controller._Controller__effectors[objectID]
        
    #Sets the Effector state to on
    def switchOn(self) -> None:
        self.object.switchOn()
    
    #Sets the Effector state to off
    def switchOff(self) -> None:
        self.object.switchOff()

    #Returns the Effector state
    def isOn(self) -> bool:
        return self.object.isOn()

class LED(Effector):
    #Switches between the on and off state
    def toggle(self) -> None:
        self.object.toggle()

    #Returns the current colour of the led
    def getColour(self) -> bool:
        return self.object.getColour()

class LCD(Effector):
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
    def putc(self, s: str) -> None:
        self.object.put(s)

    def __lshift__(self, obj) -> None:
        for c in obj:
            self.putc(c)

class Sensor(BaseClass):
    def __init__(self, controller : Controller, objectID : str):
        super(Sensor, self).__init__(controller)
        self.object = self.Controller._Controller__sensors[objectID]

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
    #Sets a singel char in the keypad (keypress controllerulation)
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

class Factory:
    def __init__(self, controller : Controller):
        self.Controller = controller

    def make(self, instType, *instArgs):
        if not issubclass(instType, BaseClass):
            raise TypeError("Class instance" + str(instType) + " does not have a valid base class.")

        #targetclass = cls.capitalize()
        inst = globals()[instType.__name__](self.Controller, *instArgs)

        #if not isinstance(inst, BaseClass):
        #    raise ValueError("Class instance" + str(instType) + " does not have a valid base class.")

        
        return inst


