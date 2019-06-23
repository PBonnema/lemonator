# pylint: disable=no-self-use, missing-docstring
from unittest import TestCase

import Constants
import CustomController
import Simulator
import SimulatorInterface

def updateSim(simulator):
    simulator._Simulator__plant.update()
    simulator._Simulator__controller.update()
    simulator._Simulator__monitor.update()

class TestStateTransitions(TestCase):
    def setUp(self):
        self.sim = Simulator.Simulator(False)

        # These variables are there for convenience
        self.vesselMix = self.sim._Simulator__plant._vessels['mix']
        self.vesselA = self.sim._Simulator__plant._vessels['a']
        self.vesselB = self.sim._Simulator__plant._vessels['b']

        # Create effector objects
        self.pumpA = self.sim._Simulator__plant._effectors['pumpA']
        self.pumpB = self.sim._Simulator__plant._effectors['pumpB']
        self.valveA = self.sim._Simulator__plant._effectors['valveA']
        self.valveB = self.sim._Simulator__plant._effectors['valveB']
        self.heater = self.sim._Simulator__plant._effectors['heater']

        # Create LED's objects
        self.ledRedA = self.sim._Simulator__plant._effectors['redA']
        self.ledGreenA = self.sim._Simulator__plant._effectors['greenA']
        self.ledRedB = self.sim._Simulator__plant._effectors['redB']
        self.ledGreenB = self.sim._Simulator__plant._effectors['greenB']
        self.ledGreenM = self.sim._Simulator__plant._effectors['greenM']
        self.ledYellowM = self.sim._Simulator__plant._effectors['yellowM']

        # Create sensors objects
        self.colour = self.sim._Simulator__plant._sensors['colour']
        self.temperature = self.sim._Simulator__plant._sensors['temp']
        self.level = self.sim._Simulator__plant._sensors['level']
        self.cup = self.sim._Simulator__plant._sensors['presence']

        # Create UI objects
        self.lcd = self.sim._Simulator__plant._effectors['lcd']
        self.keypad = self.sim._Simulator__plant._sensors['keypad']

        Interface = SimulatorInterface.SimulatorInterface
        self.ctl = CustomController.Controller(
            Interface.Effector(self.pumpA),
            Interface.Effector(self.pumpB),
            Interface.Effector(self.valveA),
            Interface.Effector(self.valveB),
            Interface.Effector(self.heater),
            Interface.LED(self.ledRedA),
            Interface.LED(self.ledGreenA),
            Interface.LED(self.ledRedB),
            Interface.LEDGreen(self.ledGreenB),
            Interface.LEDGreen(self.ledGreenM),
            Interface.LEDYellow(self.ledYellowM),
            Interface.Sensor(self.colour),
            Interface.Sensor(self.temperature),
            Interface.Sensor(self.level),
            Interface.PresenceSensor(self.cup),
            Interface.Keypad(self.keypad),
            Interface.LCD(self.lcd))
        self.sim._Simulator__controller = self.ctl
        self.ctl.prepare()

    def test_controller_view_stats_without_dispense_action(self):
        self.keypad.push('B')
        updateSim(self.sim)
        updateSim(self.sim)

        self.assertEqual(self.ctl.fault, CustomController.Faults.NONE)
        self.assertEqual(self.ctl.state, CustomController.States.DISPLAY_STATS)

        self.assertEqual(
            list(self.lcd.getLines())[2].strip(),
            f"{int(Constants.liquidMax)} ml <|> {int(Constants.liquidMax)} ml")

    def test_controller_check_stats_after_dispense(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)
        self.keypad.push('2')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)
        self.keypad.push('1')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

        for _ in range(100):
            updateSim(self.sim)

        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

        self.keypad.push('B')
        updateSim(self.sim)
        updateSim(self.sim)

        self.assertEqual(self.ctl.state, CustomController.States.DISPLAY_STATS)
        self.assertEqual(list(self.lcd.getLines())[2].strip(), "1980 ml <|> 1990 ml")

        self.assertEqual(self.ctl.liquidLevelWater, 1980)
        self.assertEqual(self.ctl.liquidLevelSyrup, 1990)