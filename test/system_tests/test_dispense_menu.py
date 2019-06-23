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

    def test_controller_start_press(self):
        # Press the A/start button
        self.keypad.push('A')

        updateSim(self.sim)

        self.assertEqual(
            self.ctl.state, CustomController.States.WAITING_FOR_CUP)

    def test_controller_wait_for_cup(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)

        self.assertEqual(
            self.ctl.state, CustomController.States.WAITING_USER_SELECTION_ONE)

    def test_controller_select_amount(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)

        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.keypad.push('2')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(self.ctl.inputTargetLevelSyrup, 20)
        self.assertEqual(self.ctl.inputTargetLevelWater, 50)

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

    def test_controller_select_zero_amount(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)

        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(
            self.ctl.fault, CustomController.Faults.SELECTION_INVALID)

    def test_controller_select_wrong_amount_water(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)

        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_WATER_SHORTAGE)

    def test_controller_select_wrong_amount_syrup(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)

        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('5')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_SYRUP_SHORTAGE)

    def test_display_waiting_for_cup_state(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(False)
        updateSim(self.sim)
        self.assertEqual(self.ctl.state, CustomController.States.WAITING_FOR_CUP)
        self.assertEqual(list(self.lcd.getLines())[2].strip(), "Please place a cup")
        self.assertEqual(list(self.lcd.getLines())[3].strip(), "to continue...")

    def test_display_dispensing_water_shortage_fault(self):
        self.ctl.fault = CustomController.Faults.DISPENSING_WATER_SHORTAGE
        updateSim(self.sim)
        self.assertEqual(list(self.lcd.getLines())[2].strip(), "Water shortage.")

    def test_display_dispensing_syrup_shortage_fault(self):
        self.ctl.fault = CustomController.Faults.DISPENSING_SYRUP_SHORTAGE
        updateSim(self.sim)
        self.assertEqual(list(self.lcd.getLines())[2].strip(), "Syrup shortage.")

    def test_display_selection_temp_too_high_fault(self):
        self.ctl.fault = CustomController.Faults.SELECTION_TEMP_TOO_HIGH
        updateSim(self.sim)
        self.assertEqual(list(self.lcd.getLines())[2].strip(), "Input too high.")

    def test_display_selection_invalid_fault(self):
        self.ctl.fault = CustomController.Faults.SELECTION_INVALID
        updateSim(self.sim)
        self.assertEqual(list(self.lcd.getLines())[2].strip(), "Invalid selection.")