from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch, call

import Simulator
import SimulatorInterface
import CustomController
import Gui
import Constants

from enum import Enum

# Here is the simulator assigned
Interface = SimulatorInterface.SimulatorInterface

# For now, we only test out pumps, valves, displays, keypad and the heater. LED's are out of scope for now...


class TestStateTransitions(TestCase):
    def setUp(self):
        self.sim = Simulator.Simulator(False)

        self.ctl = CustomController.Controller(
            self.sim._Simulator__plant._sensors, self.sim._Simulator__plant._effectors, Interface)

    def test_controller_init_actuator_and_effector_state(self):
        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

        self.assertFalse(self.ctl.pumpA.isOn())
        self.assertFalse(self.ctl.pumpB.isOn())
        self.assertFalse(self.ctl.valveA.isOn())
        self.assertFalse(self.ctl.valveB.isOn())
        self.assertFalse(self.ctl.heater.isOn())
        self.assertFalse(self.ctl.cup.readValue())

        self.assertEqual(self.ctl.latestKeypress, None)

    def test_controller_init_state_vars(self):
        self.assertEqual(self.ctl.liquidLevelWater, Constants.liquidMax)
        self.assertEqual(self.ctl.liquidLevelSyrup, Constants.liquidMax)
        self.assertEqual(self.ctl.targetLevelWater, "")
        self.assertEqual(self.ctl.targetLevelSyrup, "")
        self.assertEqual(self.ctl.targetLevelSyrupCup, 0)
        self.assertEqual(self.ctl.targetLevelWaterCup, 0)
        self.assertEqual(self.ctl.targetHeat, "")

    def test_controller_init_fault_state(self):
        self.assertEqual(self.ctl.fault, CustomController.Faults.NONE)

    def test_lcd_is_clear(self):
        lcdLines = self.ctl.lcd.getLines()
        self.assertIsInstance(lcdLines, map)

        for lcdLine in lcdLines:
            self.assertEqual(lcdLine, ' ' * 20)

    def test_controller_invalid_key_press(self):
        self.ctl.keypad.push('Z')

        self.ctl.update()

        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

    def test_controller_start_press(self):
        # Press the A/start button
        self.ctl.keypad.push('A')

        # Run update
        self.ctl.update()

        self.assertEqual(
            self.ctl.state, CustomController.States.WAITING_FOR_CUP)

    def test_controller_wait_for_cup(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()

        self.assertEqual(
            self.ctl.state, CustomController.States.WAITING_USER_SELECTION_ONE)

    def test_controller_select_amount(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()

        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.ctl.keypad.push('2')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertEqual(self.ctl.targetLevelWater, 0.5)
        self.assertEqual(self.ctl.targetLevelSyrup, 0.2)

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING)

    def test_controller_select_zero_amount(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()

        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertEqual(
            self.ctl.fault, CustomController.Faults.SELECTION_INVALID)

    def test_controller_dispensing(self):
        pass

    def test_controller_dispensing_fault_cup_removed(self):
        pass
