from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch

import Constants
import CustomController
import Simulator
import SimulatorInterface

# Here is the simulator assigned
Interface = SimulatorInterface.SimulatorInterface

# For now, we only test the pumps, valves, displays, keypad and the heater. LED's are out of scope for now...


class TestStateTransitions(TestCase):
    def setUp(self):
        self.sim = Simulator.Simulator(False)
        self.ctl = CustomController.Controller(
            self.sim._Simulator__plant._sensors, self.sim._Simulator__plant._effectors, Interface)

    def test_controller_init_actuator_and_effector_state(self):#
        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

        self.assertFalse(self.ctl.pumpA.isOn())
        self.assertFalse(self.ctl.pumpB.isOn())
        self.assertFalse(self.ctl.valveA.isOn())
        self.assertFalse(self.ctl.valveB.isOn())
        self.assertFalse(self.ctl.heater.isOn())
        self.assertFalse(self.ctl.cup.readValue())

        self.assertEqual(self.ctl.latestKeypress, None)

    def test_controller_init_state_vars(self):#
        self.assertEqual(self.ctl.liquidLevelWater, Constants.liquidMax)
        self.assertEqual(self.ctl.liquidLevelSyrup, Constants.liquidMax)
        self.assertEqual(self.ctl.inputTargetLevelWater, "")
        self.assertEqual(self.ctl.inputTargetLevelSyrup, "")
        self.assertEqual(self.ctl.targetHeat, "")

    def test_controller_init_fault_state(self):#
        self.assertEqual(self.ctl.fault, CustomController.Faults.NONE)

    def test_lcd_is_clear(self):#
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

        self.assertEqual(self.ctl.inputTargetLevelSyrup, 20)
        self.assertEqual(self.ctl.inputTargetLevelWater, 50)

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

    def test_controller_select_zero_amount(self):#
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

    def test_controller_select_too_high_heater(self):#
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
            self.ctl.fault, CustomController.Faults.SELECTION_TEMP_TOO_HIGH)

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

        for _ in range(150):
            self.ctl.update()


        self.assertEqual(self.ctl.liquidLevelWater, 1900)
        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

    def test_controller_dispensing_fault_cup_removed(self):#
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

    def test_controller_select_wrong_amount_water(self):#
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

    def test_controller_select_wrong_amount_syrup(self):#
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
        self.ctl.update()

        self.assertEqual(self.ctl.state, CustomController.States.DISPLAY_STATS)
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "1980 ml <|> 1990 ml")

        self.assertEqual(self.ctl.liquidLevelWater, 1980)
        self.assertEqual(self.ctl.liquidLevelSyrup, 1990)

    def test_controller_cup_contents(self):
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()
        self.ctl.keypad.push('9')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()
        self.ctl.keypad.push('9')
        self.ctl.update()
        self.ctl.keypad.push('0')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

        for _ in range(200):
            self.ctl.update()
        
        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

        self.assertAlmostEqual(self.ctl.level.readValue(), 280/Constants.levelVoltageFactor, 1)


    def test_controller_heater_input(self):
        self.ctl.keypad.push('D')
        self.ctl.update()

        self.ctl.cup.set(True)
        self.ctl.update()
        self.ctl.keypad.push('8')
        self.ctl.update()
        self.ctl.keypad.push('9')
        self.ctl.update()
        self.ctl.keypad.push('#')
        self.ctl.update()

        self.assertAlmostEqual(self.ctl.targetHeat, 89.0)

    def test_display_idle_state(self):#
        self.ctl.update()
        self.assertEqual(self.ctl.state, CustomController.States.IDLE)
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "A = Start, B = Stats")
        self.assertEqual(list(self.ctl.lcd.getLines())[3].strip(), "D = Heat")

    def test_display_waiting_for_cup_state(self):#
        self.ctl.keypad.push('A')
        self.ctl.update()

        self.ctl.cup.set(False)
        self.ctl.update()
        self.assertEqual(self.ctl.state, CustomController.States.WAITING_FOR_CUP)
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "Please place a cup")
        self.assertEqual(list(self.ctl.lcd.getLines())[3].strip(), "to continue...")

    def test_display_dispensing_cup_removed_fault(self):#
        self.ctl.fault = CustomController.Faults.DISPENSING_CUP_REMOVED
        self.ctl.update()
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "Cup removed.")

    def test_display_dispensing_water_shortage_fault(self):#
        self.ctl.fault = CustomController.Faults.DISPENSING_WATER_SHORTAGE
        self.ctl.update()
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "Water shortage.")
    
    def test_display_dispensing_syrup_shortage_fault(self):#
        self.ctl.fault = CustomController.Faults.DISPENSING_SYRUP_SHORTAGE
        self.ctl.update()
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "Syrup shortage.")

    def test_display_selection_temp_too_high_fault(self):#
        self.ctl.fault = CustomController.Faults.SELECTION_TEMP_TOO_HIGH
        self.ctl.update()
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "Input too high.")

    def test_display_selection_invalid_fault(self):#
        self.ctl.fault = CustomController.Faults.SELECTION_INVALID
        self.ctl.update()
        self.assertEqual(list(self.ctl.lcd.getLines())[2].strip(), "Invalid selection.")

    def test_start_water_pump_pumpA_already_on_only_one_can_be_on_true(self):#
        self.ctl.pumpA.switchOn()
        self.ctl.startWaterPump(onlyOneCanBeOn=True)
        self.assertEqual(self.ctl.pumpA.isOn(), True)
        self.assertEqual(self.ctl.valveA.isOn(), False)
        self.assertEqual(self.ctl.pumpB.isOn(), False)
        self.assertEqual(self.ctl.valveB.isOn(), True)
    
    def test_start_water_pump_valveA_already_on_only_one_can_be_on_true(self):#
        self.ctl.valveA.switchOn()
        self.ctl.startWaterPump(True)
        self.assertEqual(self.ctl.pumpA.isOn(), True)
        self.assertEqual(self.ctl.valveA.isOn(), False)
        self.assertEqual(self.ctl.pumpB.isOn(), False)
        self.assertEqual(self.ctl.valveB.isOn(), True)
    
    def test_start_water_pump_only_one_can_be_on_true(self):#
        self.ctl.startWaterPump(onlyOneCanBeOn=True)
        self.assertEqual(self.ctl.pumpA.isOn(), True)
        self.assertEqual(self.ctl.valveA.isOn(), False)
        self.assertEqual(self.ctl.pumpB.isOn(), False)
        self.assertEqual(self.ctl.valveB.isOn(), True)

    def test_start_syrup_pump_only_one_can_be_on_true(self):#
        self.ctl.startSyrupPump(onlyOneCanBeOn=True)
        self.assertEqual(self.ctl.pumpB.isOn(), True)
        self.assertEqual(self.ctl.valveB.isOn(), False)
        self.assertEqual(self.ctl.pumpA.isOn(), False)
        self.assertEqual(self.ctl.valveA.isOn(), True)

    def test_start_syrup_pump_pumpB_already_on_only_one_can_be_on_true(self):#
        self.ctl.pumpB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=True)
        self.assertEqual(self.ctl.pumpB.isOn(), True)
        self.assertEqual(self.ctl.valveB.isOn(), False)
        self.assertEqual(self.ctl.pumpA.isOn(), False)
        self.assertEqual(self.ctl.valveA.isOn(), True)
    
    def test_start_syrup_pump_valveB_already_on_only_one_can_be_on_true(self):#
        self.ctl.valveB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=True)
        self.assertEqual(self.ctl.pumpB.isOn(), True)
        self.assertEqual(self.ctl.valveB.isOn(), False)
        self.assertEqual(self.ctl.pumpA.isOn(), False)
        self.assertEqual(self.ctl.valveA.isOn(), True)

    def test_start_water_pump_pumpA_already_on_only_one_can_be_on_false(self):#
        self.ctl.pumpA.switchOn()
        self.ctl.startWaterPump(onlyOneCanBeOn=False)
        self.assertEqual(self.ctl.pumpA.isOn(), True)
        self.assertEqual(self.ctl.valveA.isOn(), False)
        
    def test_start_water_pump_valveA_already_on_only_one_can_be_on_false(self):#
        self.ctl.valveA.switchOn()
        self.ctl.startWaterPump(onlyOneCanBeOn=False)
        self.assertEqual(self.ctl.pumpA.isOn(), True)
        self.assertEqual(self.ctl.valveA.isOn(), False)

    def test_start_water_pump_only_one_can_be_on_false(self):#
        self.ctl.startWaterPump(onlyOneCanBeOn=False)
        self.assertEqual(self.ctl.pumpA.isOn(), True)
        self.assertEqual(self.ctl.valveA.isOn(), False)

    def test_start_syrup_pump_only_one_can_be_on_false(self):#
        self.ctl.startSyrupPump(onlyOneCanBeOn=False)
        self.assertEqual(self.ctl.pumpB.isOn(), True)
        self.assertEqual(self.ctl.valveB.isOn(), False)

    def test_start_syrup_pump_pumpB_already_on_only_one_can_be_on_false(self):#
        self.ctl.pumpB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=False)
        self.assertEqual(self.ctl.pumpB.isOn(), True)
        self.assertEqual(self.ctl.valveB.isOn(), False)
    
    def test_start_syrup_pump_valveB_already_on_only_one_can_be_on_false(self):#
        self.ctl.valveB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=False)
        self.assertEqual(self.ctl.pumpB.isOn(), True)
        self.assertEqual(self.ctl.valveB.isOn(), False)
    
    def test_update_leds_pumpA_on_valveA_off(self):
        self.ctl.pumpA.switchOn()
        self.ctl.valveA.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledGreenA.isOn(), True)
        self.assertEqual(self.ctl.ledRedA.isOn(), False)

    def test_update_leds_pumpA_on_valveA_on(self):
        self.ctl.pumpA.switchOn()
        self.ctl.valveA.switchOn()
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledGreenA.isOn(), False)
        self.assertEqual(self.ctl.ledRedA.isOn(), True)

    def test_update_leds_pumpA_off_valveA_off(self):
        self.ctl.pumpA.switchOff()
        self.ctl.valveA.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledGreenA.isOn(), False)
        self.assertEqual(self.ctl.ledRedA.isOn(), True)

    def test_update_leds_pumpB_on_valveB_off(self):
        self.ctl.pumpB.switchOn()
        self.ctl.valveB.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledGreenB.isOn(), True)
        self.assertEqual(self.ctl.ledRedB.isOn(), False)

    def test_update_leds_pumpB_on_valveB_on(self):
        self.ctl.pumpB.switchOn()
        self.ctl.valveB.switchOn()
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledGreenB.isOn(), False)
        self.assertEqual(self.ctl.ledRedB.isOn(), True)

    def test_update_leds_pumpB_off_valveB_off(self):
        self.ctl.pumpB.switchOff()
        self.ctl.valveB.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledGreenB.isOn(), False)
        self.assertEqual(self.ctl.ledRedB.isOn(), True)

    def test_update_leds_pumpA_off_valveA_off_pumpB_off_valveB_off_cup_true(self):
        self.ctl.pumpA.switchOff()
        self.ctl.valveA.switchOff()
        self.ctl.pumpB.switchOff()
        self.ctl.valveB.switchOff()
        self.ctl.cup.set(True)
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledYellowM.isOn(), True)
        self.assertEqual(self.ctl.ledGreenM.isOn(), False)
    
    def test_update_leds_pumpA_off_valveA_off_pumpB_off_valveB_off_cup_false(self):
        self.ctl.pumpA.switchOff()
        self.ctl.valveA.switchOff()
        self.ctl.pumpB.switchOff()
        self.ctl.valveB.switchOff()
        self.ctl.cup.set(False)
        self.ctl.updateLeds()
        self.assertEqual(self.ctl.ledYellowM.isOn(), True)
        self.assertEqual(self.ctl.ledGreenM.isOn(), False)
    
    def test_update_leds_pumpA_on_valveA_off_pumpB_on_valveB_off_cup_false(self):
        self.ctl.pumpA.switchOn()
        self.ctl.valveA.switchOff()
        self.ctl.pumpB.switchOn()
        self.ctl.valveB.switchOff()
        self.ctl.cup.set(False)
        self.ctl.updateLeds()

        self.assertEqual(self.ctl.ledYellowM.isOn(), True)
        self.assertEqual(self.ctl.ledGreenM.isOn(), False)

    def test_update_leds_pumpA_on_valveA_off_pumpB_on_valveB_off_cup_true(self):
        self.ctl.pumpA.switchOn()
        self.ctl.valveA.switchOff()
        self.ctl.pumpB.switchOn()
        self.ctl.valveB.switchOff()
        self.ctl.cup.set(True)
        self.ctl.updateLeds()

        self.assertEqual(self.ctl.ledYellowM.isOn(), False)
        self.assertEqual(self.ctl.ledGreenM.isOn(), True)

    def test_update_leds_pumpA_on_valveA_on_pumpB_on_valveB_on_cup_true(self):
        self.ctl.pumpA.switchOn()
        self.ctl.valveA.switchOn()
        self.ctl.pumpB.switchOn()
        self.ctl.valveB.switchOn()
        self.ctl.cup.set(True)
        self.ctl.updateLeds()

        self.assertEqual(self.ctl.ledYellowM.isOn(), True)
        self.assertEqual(self.ctl.ledGreenM.isOn(), False)
    
    def test_update_leds_pumpA_on_valveA_on_pumpB_on_valveB_on_cup_false(self):
        self.ctl.pumpA.switchOn()
        self.ctl.valveA.switchOn()
        self.ctl.pumpB.switchOn()
        self.ctl.valveB.switchOn()
        self.ctl.cup.set(False)
        self.ctl.updateLeds()

        self.assertEqual(self.ctl.ledYellowM.isOn(), True)
        self.assertEqual(self.ctl.ledGreenM.isOn(), False)

    def test_shutfluids_pumpA_on_pumpB_on(self):
        self.ctl.pumpA.switchOn()
        self.ctl.pumpB.switchOn()
        self.ctl.shutFluid()
        self.assertEqual(self.ctl.pumpA.isOn(), False)
        self.assertEqual(self.ctl.pumpB.isOn(), False)
        self.assertEqual(self.ctl.valveA.isOn(), True)
        self.assertEqual(self.ctl.valveB.isOn(), True)

    def test_validate_cup_appearance_cup_true(self):
        self.ctl.cup.set(True)
        self.assertEqual(self.ctl.validateCupAppearance(), True)
        self.assertEqual(self.ctl.fault, CustomController.Faults.NONE)

    def test_validate_cup_appearance_cup_false(self):
        self.ctl.cup.set(False)
        self.assertEqual(self.ctl.validateCupAppearance(), False)
        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_CUP_REMOVED)

    def test_syrup_false_water_true(self):
        self.ctl.pumpA.switchOn()
        self.ctl.pumpB.switchOn()
        self.ctl.liquidLevelSyrup = 0
        self.ctl.liquidLevelWater = 1000
        self.ctl.update()
        self.ctl.update()

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_SYRUP_SHORTAGE)

    def test_syrup_true_water_false(self):
        self.ctl.pumpA.switchOn()
        self.ctl.pumpB.switchOn()
        self.ctl.liquidLevelSyrup = 1000
        self.ctl.liquidLevelWater = 0
        self.ctl.update()
        self.ctl.update()

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_WATER_SHORTAGE)
 