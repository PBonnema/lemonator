from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch, call

import Simulator
import SimulatorInterface
import CustomController
import Gui
import Constants

from time import sleep

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
        self.assertEqual(self.ctl.inputTargetLevelWater, "")
        self.assertEqual(self.ctl.inputTargetLevelSyrup, "")
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

        #self.assertEqual(self.ctl.targetLevelWater, 52.72727272727273)
        self.assertEqual(self.ctl.inputTargetLevelSyrup, 20)
        #self.assertEqual(self.ctl.targetLevelSyrup, 22.727272727272727)
        self.assertEqual(self.ctl.inputTargetLevelWater, 50)

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

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

    def test_controller_select_too_high_heater(self):
        self.ctl.keypad.push('D')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()
        self.ctl.keypad.push('1')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertEqual(
            self.ctl.fault, CustomController.Faults.SELECTION_INVALID)

    def test_controller_dispensing_liquid_updates_vessel(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()
        self.ctl.keypad.push('1')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()
        self.ctl.keypad.push('1')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()
        self.assertEqual(self.ctl.liquidLevelWater, 2000)

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

        temp = self.ctl.liquidLevelWater

        for _ in range(1100):
            self.ctl.update()

        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

    def test_controller_dispensing_fault_cup_removed(self):
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

        self.ctl.cup.set(False)
        self.ctl.update()

        self.assertEqual(
            self.ctl.fault, CustomController.Faults.DISPENSING_CUP_REMOVED)

    def test_controller_view_stats_without_dispense_action(self):
        self.ctl.keypad.push('B')
        self.ctl.update()
        self.ctl.update()

        self.assertEqual(self.ctl.fault, CustomController.Faults.NONE)
        self.assertEqual(self.ctl.state, CustomController.States.DISPLAY_STATS)

        self.assertEqual(list(self.ctl.lcd.getLines())
                         [2].strip(), str(int(Constants.liquidMax)) + " ml <|> " + str(int(Constants.liquidMax)) + " ml")

    def test_controller_select_wrong_amount_water(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()

        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_WATER_SHORTAGE)
    
    def test_controller_select_wrong_amount_syrup(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()

        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('5')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_SYRUP_SHORTAGE)
    
        
    def test_controller_check_stats_after_dispense(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()
        self.ctl.keypad.push('2')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()
        self.ctl.keypad.push('1')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

        for _ in range(100):
            self.ctl.update()
        
        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

        self.ctl.keypad.push('B')
        self.ctl.update()

        self.assertEqual(self.ctl.state, CustomController.States.DISPLAY_STATS)
        #self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "1980 ml <|> 1990 ml")
        self.assertEqual(self.ctl.liquidLevelWater, 1980)
        self.assertEqual(self.ctl.liquidLevelSyrup, 1990)