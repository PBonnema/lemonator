import argparse
import sys
import time

import CustomController
import Gui
import HardwareInterface
import Simulator
import SimulatorInterface

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Controls the Lemonator.')
    parser.add_argument(
        '--sim', help='Run on the simulator.', action='store_true')
    parser.add_argument(
        '--hw', help='Run on the hardware.', action='store_true')

    args = parser.parse_args()

    if (args.sim and args.hw) or (not args.sim and not args.hw):
        print("Please use --sim or --hw argument.")
        exit(1)

    if args.sim:
        # A bit of explaining here is needed, because I want to overwrite the GUI with our custom controller.
        # You don't want the simulator to make the GUI for you. So the GUI bool is set to False.
        simulator = Simulator.Simulator(False)

        Interface = SimulatorInterface.SimulatorInterface
        # ======================== SIMULATOR DEFINTIONS (SOFTWARE INTERFACE) ========================
        # Create effector objects
        pumpA = Interface.Effector(simulator._Simulator__plant._effectors['pumpA'])
        pumpB = Interface.Effector(simulator._Simulator__plant._effectors['pumpB'])
        valveA = Interface.Effector(simulator._Simulator__plant._effectors['valveA'])
        valveB = Interface.Effector(simulator._Simulator__plant._effectors['valveB'])
        heater = Interface.Effector(simulator._Simulator__plant._effectors['heater'])

        # Create LED's objects
        ledRedA = Interface.LED(simulator._Simulator__plant._effectors['redA'])
        ledGreenA = Interface.LED(simulator._Simulator__plant._effectors['greenA'])
        ledRedB = Interface.LED(simulator._Simulator__plant._effectors['redB'])
        ledGreenB = Interface.LEDGreen(simulator._Simulator__plant._effectors['greenB'])
        ledGreenM = Interface.LEDGreen(simulator._Simulator__plant._effectors['greenM'])
        ledYellowM = Interface.LEDYellow(simulator._Simulator__plant._effectors['yellowM'])

        # Create sensors objects
        colour = Interface.Sensor(simulator._Simulator__plant._sensors['colour'])
        temperature = Interface.Sensor(simulator._Simulator__plant._sensors['temp'])
        level = Interface.Sensor(simulator._Simulator__plant._sensors['level'])
        cup = Interface.PresenceSensor(simulator._Simulator__plant._sensors['presence'])

        # Create UI objects
        keypad = Interface.Keypad(simulator._Simulator__plant._sensors['keypad'])
        lcd = Interface.LCD(simulator._Simulator__plant._effectors['lcd'])

        # Here is the Controller created with a custom interface, here you can use a SoftwareInterface or a HardwareInterface
        controllerObject = CustomController.Controller(
            pumpA, pumpB, valveA, valveB, heater, ledRedA, ledGreenA, ledRedB,
            ledGreenB, ledGreenM, ledYellowM, colour, temperature, level, cup, keypad, lcd
        )

    if args.hw:
        Interface = HardwareInterface.HardwareInterface
        # ======================== LEMONATOR PROXY DEFINTIONS (HARDWARE INTERFACE) ========================
        # Create effector objects
        pumpA = Interface.Pump('A')
        pumpB = Interface.Pump('B')
        valveA = Interface.Valve('A')
        valveB = Interface.Valve('B')
        heater = Interface.Heater()

        # Create LED's objects
        ledRedA = Interface.LED()
        ledGreenA = Interface.LED()
        ledRedB = Interface.LED()
        ledGreenB = Interface.LEDGreen()
        ledGreenM = Interface.LEDGreen()
        ledYellowM = Interface.LEDYellow()

        # Create sensors objects
        colour = Interface.ColourSensor()
        temperature = Interface.TemperatureSensor()
        level = Interface.LevelSensor()
        cup = Interface.PresenceSensor()

        # Create UI objects
        keypad = Interface.Keypad()
        lcd = Interface.LCD()

        # Here is the Controller created with a custom interface, here you can use a SoftwareInterface or a HardwareInterface
        controllerObject = CustomController.Controller(
            pumpA, pumpB, valveA, valveB, heater, ledRedA, ledGreenA, ledRedB,
            ledGreenB, ledGreenM, ledYellowM, colour, temperature, level, cup, keypad, lcd
        )

    controllerObject.prepare()

    # ======================== SIMULATOR GUI PREPERATIONS (IF REQUIRED) ========================

    if args.sim:
        simulator._Simulator__controller = controllerObject

        # Here is the GUI created. This is the GUI, that the simulator will use. Thereby it uses our custom controller.
        simulator._Simulator__gui = Gui.GUI(
            simulator._Simulator__plant,
            controllerObject,
            simulator._Simulator__monitor
        )

        # The GUI still has to be actived by the simulator.
        simulator.run()

    if args.hw:
        while True:
            try:
                time.sleep(0.5)
                controllerObject.update()

                print(controllerObject.state)
                sys.stdout.flush()
            except KeyboardInterrupt:
                exit(0)
