import Simulator
import SimulatorInterface
import HardwareInterface
import CustomController
import Gui
import time
import sys
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Controls the Lemonator.')
    parser.add_argument(
        '--sim', help='Run upon the simulator.', action='store_true')
    parser.add_argument(
        '--hw', help='Run upon the hardware.', action='store_true')

    args = parser.parse_args()

    if (args.sim and args.hw) or (not args.sim and not args.hw):
        print("Please use --sim or --hw argument.")
        exit(1)

    # A bit of explaining here is needed, because I want to overwrite the GUI with our custom controller.
    # You don't want the simulator to make the GUI for you. So the GUI bool is set to False.
    simulator = Simulator.Simulator(False)

    if args.sim:
        # Here is the simulator assigned. Choose one of the two below.
        Interface = SimulatorInterface.SimulatorInterface
        # Interface = HardwareInterface.HardwareInterface

    if args.hw:
        Interface = HardwareInterface.HardwareInterface

    # Here is the Controller created with a custom interface, here you can use a SoftwareInterface or a HardwareInterface
    controllerObject = CustomController.Controller(simulator._Simulator__plant._sensors,
                                                   simulator._Simulator__plant._effectors)

    if args.hw:
        # Create control object
        control = Interface.Factory()

    if args.sim:
        control = Interface.Factory(controllerObject)

    if args.sim:
        # ======================== SIMULATOR DEFINTIONS (SOFTWARE INTERFACE) ========================
        # Create effector objects
        controllerObject.pumpA = control.make(Interface.Effector, 'pumpA')
        controllerObject.pumpB = control.make(Interface.Effector, 'pumpB')
        controllerObject.valveA = control.make(Interface.Effector, 'valveA')
        controllerObject.valveB = control.make(Interface.Effector, 'valveB')
        controllerObject.heater = control.make(Interface.Effector, 'heater')

        # Create LED's objects
        controllerObject.ledRedA = control.make(Interface.LED, 'redA')
        controllerObject.ledGreenA = control.make(Interface.LED, 'greenA')
        controllerObject.ledRedB = control.make(Interface.LED, 'redB')
        controllerObject.ledGreenB = control.make(Interface.LED, 'greenB')
        controllerObject.ledGreenM = control.make(Interface.LED, 'greenM')
        controllerObject.ledYellowM = control.make(Interface.LED, 'yellowM')

        # Create sensors objects
        controllerObject.colour = control.make(Interface.Sensor, 'colour')
        controllerObject.temperature = control.make(Interface.Sensor, 'temp')
        controllerObject.level = control.make(Interface.Sensor, 'level')
        controllerObject.cup = control.make(
            Interface.PresenceSensor, 'presence')

        controllerObject.lcd = control.make(Interface.LCD, 'lcd')
        controllerObject.keypad = control.make(Interface.Keypad, 'keypad')

    if args.hw:
        # ======================== LEMONATOR PROXY DEFINTIONS (HARDWARE INTERFACE) ========================
        # Create effector objects
        controllerObject.pumpA = control.make(Interface.Effector)
        controllerObject.pumpB = control.make(Interface.Effector)
        controllerObject.valveA = control.make(Interface.Effector)
        controllerObject.valveB = control.make(Interface.Effector)
        controllerObject.heater = control.make(Interface.Effector)

        # Create LED's objects
        controllerObject.ledRedA = control.make(Interface.LED)
        controllerObject.ledGreenA = control.make(Interface.LED)
        controllerObject.ledRedB = control.make(Interface.LED)
        controllerObject.ledGreenB = control.make(Interface.LED)
        controllerObject.ledGreenM = control.make(Interface.LED)
        controllerObject.ledYellowM = control.make(Interface.LED)

        # Create sensors objects
        controllerObject.colour = control.make(Interface.Sensor)
        controllerObject.temperature = control.make(Interface.Sensor)
        controllerObject.level = control.make(Interface.Sensor)
        controllerObject.cup = control.make(Interface.PresenceSensor)

        # Create UI objects
        controllerObject.lcd = control.make(Interface.LCD)
        controllerObject.keypad = control.make(Interface.Keypad)

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
