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

    def test_controller_select_too_high_heater(self):
        self.keypad.push('D')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)
        self.keypad.push('1')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(
            self.ctl.fault, CustomController.Faults.SELECTION_TEMP_TOO_HIGH)

    def test_controller_heater_input(self):
        self.keypad.push('D')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)
        self.keypad.push('8')
        updateSim(self.sim)
        self.keypad.push('9')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertAlmostEqual(self.ctl.inputTargetHeat, 89.0)