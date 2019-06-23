import lemonator
import time


def ReadTemperature(hw) -> float:
    time.sleep(0.05)
    return float(int(hw.temperature.read_mc()) / 1000.0)


def DispenseWater(hw, b: bool):
    time.sleep(0.05)
    hw.water_valve.set(not b)
    time.sleep(0.05)
    hw.water_pump.set(b)


def DispenseSirup(hw, b: bool):
    time.sleep(0.05)
    hw.sirup_valve.set(not b)
    time.sleep(0.05)
    hw.sirup_pump.set(b)


def SetHeater(hw, b: bool):
    time.sleep(0.05)
    hw.heater.set(b)


def ReadDistance(hw) -> float:
    time.sleep(0.05)

    values = []
    for _i in range(5):
        val = float(hw.distance.read_mm())
        values.append(val)

    

    return 90.0 - max(values)


def IsCupPlaced(hw) -> bool:
    time.sleep(0.05)
    return bool(hw.reflex.get())


def ReadKeypad(hw) -> str:
    time.sleep(0.05)
    return str(hw.keypad.getc())


def SetYellowLED(hw, b):
    time.sleep(0.05)
    hw.led_yellow.set(b)


def SetGreenLED(hw, b):
    time.sleep(0.05)
    hw.led_green.set(b)


def LCDPut(hw, s: str):
    for ch in s:
        hw.lcd.putc(ch)
        # time.sleep(0.01)


try:

    print("Starting lemonator...")
    hw = lemonator.lemonator(2)  # COM3
    led = hw.led_yellow
except:
    exit(0)

time.sleep(3)

SetYellowLED(hw, False)
SetGreenLED(hw, True)

time.sleep(0.5)

# sirup_pump = hw.sirup_pump
# sirup_valve = hw.sirup_valve

# water_pump = hw.water_pump
# water_valve = hw.water_valve
# hw.lcd.putc('A')
LCDPut(hw, "?Hello World!")


temperature = hw.temperature

print("Temperature: ")
dump = temperature.read_mc()
print(int(dump) / 1000.0)  # Temp

DispenseWater(hw, False)
DispenseSirup(hw, False)


DispenseWater(hw, True)
for _i in range(40):
    print(ReadDistance(hw))
    time.sleep(0.5)

DispenseWater(hw, False)

DispenseSirup(hw, True)
time.sleep(3)
DispenseSirup(hw, False)

print("Temperature: ")
print(ReadTemperature(hw))

##print("Heater on...")
##SetHeater(hw, True)

##time.sleep(25)

##print("Heater off...")
##SetHeater(hw, False)

print("Temperature: ")
print(ReadTemperature(hw))

print("Do something on the keypad...")
while True:
    print("Key: ")
    print(ReadKeypad(hw))

    print("Distance: ")
    print(ReadDistance(hw))
