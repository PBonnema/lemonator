import lemonator
import time

try:

    print("Starting lemonator...")
    hw = lemonator.lemonator(1)  # COM2
    led = hw.led_yellow
except:
    exit(0)

temperature = hw.temperature

print("Temperature: ")
print(temperature.read_mc())
while True:
    try:
        led.set(1)
        time.sleep(0.5)
        led.set(0)
        time.sleep(0.5)
    except:
        exit(1)
