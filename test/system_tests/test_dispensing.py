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

    def test_controller_dispensing_liquid_updates_vessel(self):
        self.keypad.push('A')
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
        self.keypad.push('1')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(self.ctl.liquidLevelWater, 2000)
        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

        for _ in range(150):
            updateSim(self.sim)

        self.assertEqual(self.ctl.liquidLevelWater, 1900)
        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

    def test_controller_cup_contents(self):
        self.keypad.push('A')
        updateSim(self.sim)

        self.vesselMix.setPresence(True)
        updateSim(self.sim)
        self.keypad.push('9')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)
        self.keypad.push('9')
        updateSim(self.sim)
        self.keypad.push('0')
        updateSim(self.sim)
        self.keypad.push('#')
        updateSim(self.sim)

        self.assertEqual(self.ctl.state, CustomController.States.DISPENSING_WATER)

        for _ in range(200):
            updateSim(self.sim)

        self.assertEqual(self.ctl.state, CustomController.States.IDLE)

        self.assertAlmostEqual(self.level.readValue(), 280/Constants.levelVoltageFactor, 1)

    def test_controller_dispensing_fault_cup_removed(self):
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

        self.vesselMix.setPresence(False)
        updateSim(self.sim)

        self.assertEqual(
            self.ctl.fault, CustomController.Faults.DISPENSING_CUP_REMOVED)

    def test_display_dispensing_cup_removed_fault(self):
        self.ctl.fault = CustomController.Faults.DISPENSING_CUP_REMOVED
        updateSim(self.sim)
        self.assertEqual(list(self.lcd.getLines())[2].strip(), "Cup removed.")

    def test_start_water_pump_pumpA_already_on_only_one_can_be_on_true(self):
        self.pumpA.switchOn()
        self.ctl.startWaterPump(onlyOneCanBeOn=True)
        self.assertEqual(self.pumpA.isOn(), True)
        self.assertEqual(self.valveA.isOn(), False)
        self.assertEqual(self.pumpB.isOn(), False)
        self.assertEqual(self.valveB.isOn(), True)

    def test_start_water_pump_valveA_already_on_only_one_can_be_on_true(self):
        self.valveA.switchOn()
        self.ctl.startWaterPump(True)
        self.assertEqual(self.pumpA.isOn(), True)
        self.assertEqual(self.valveA.isOn(), False)
        self.assertEqual(self.pumpB.isOn(), False)
        self.assertEqual(self.valveB.isOn(), True)

    def test_start_water_pump_only_one_can_be_on_true(self):
        self.ctl.startWaterPump(onlyOneCanBeOn=True)
        self.assertEqual(self.pumpA.isOn(), True)
        self.assertEqual(self.valveA.isOn(), False)
        self.assertEqual(self.pumpB.isOn(), False)
        self.assertEqual(self.valveB.isOn(), True)

    def test_start_syrup_pump_only_one_can_be_on_true(self):
        self.ctl.startSyrupPump(onlyOneCanBeOn=True)
        self.assertEqual(self.pumpB.isOn(), True)
        self.assertEqual(self.valveB.isOn(), False)
        self.assertEqual(self.pumpA.isOn(), False)
        self.assertEqual(self.valveA.isOn(), True)

    def test_start_syrup_pump_pumpA_already_on_only_one_can_be_on_true(self):
        self.pumpB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=True)
        self.assertEqual(self.pumpB.isOn(), True)
        self.assertEqual(self.valveB.isOn(), False)
        self.assertEqual(self.pumpA.isOn(), False)
        self.assertEqual(self.valveA.isOn(), True)

    def test_start_syrup_pump_valveA_already_on_only_one_can_be_on_true(self):
        self.valveB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=True)
        self.assertEqual(self.pumpB.isOn(), True)
        self.assertEqual(self.valveB.isOn(), False)
        self.assertEqual(self.pumpA.isOn(), False)
        self.assertEqual(self.valveA.isOn(), True)

    def test_start_water_pump_pumpA_already_on_only_one_can_be_on_false(self):
        self.pumpA.switchOn()
        self.ctl.startWaterPump(onlyOneCanBeOn=False)
        self.assertEqual(self.pumpA.isOn(), True)
        self.assertEqual(self.valveA.isOn(), False)

    def test_start_water_pump_valveA_already_on_only_one_can_be_on_false(self):
        self.valveA.switchOn()
        self.ctl.startWaterPump(onlyOneCanBeOn=False)
        self.assertEqual(self.pumpA.isOn(), True)
        self.assertEqual(self.valveA.isOn(), False)

    def test_start_water_pump_only_one_can_be_on_false(self):
        self.ctl.startWaterPump(onlyOneCanBeOn=False)
        self.assertEqual(self.pumpA.isOn(), True)
        self.assertEqual(self.valveA.isOn(), False)

    def test_start_syrup_pump_only_one_can_be_on_false(self):
        self.ctl.startSyrupPump(onlyOneCanBeOn=False)
        self.assertEqual(self.pumpB.isOn(), True)
        self.assertEqual(self.valveB.isOn(), False)

    def test_start_syrup_pump_pumpA_already_on_only_one_can_be_on_false(self):
        self.pumpB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=False)
        self.assertEqual(self.pumpB.isOn(), True)
        self.assertEqual(self.valveB.isOn(), False)

    def test_start_syrup_pump_valveA_already_on_only_one_can_be_on_false(self):
        self.valveB.switchOn()
        self.ctl.startSyrupPump(onlyOneCanBeOn=False)
        self.assertEqual(self.pumpB.isOn(), True)
        self.assertEqual(self.valveB.isOn(), False)

    def test_update_leds_pumpA_on_valveA_off(self):
        self.pumpA.switchOn()
        self.valveA.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ledGreenA.isOn(), True)
        self.assertEqual(self.ledRedA.isOn(), False)

    def test_update_leds_pumpA_on_valveA_on(self):
        self.pumpA.switchOn()
        self.valveA.switchOn()
        self.ctl.updateLeds()
        self.assertEqual(self.ledGreenA.isOn(), False)
        self.assertEqual(self.ledRedA.isOn(), True)

    def test_update_leds_pumpA_off_valveA_off(self):
        self.pumpA.switchOff()
        self.valveA.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ledGreenA.isOn(), False)
        self.assertEqual(self.ledRedA.isOn(), True)

    def test_update_leds_pumpB_on_valveB_off(self):
        self.pumpB.switchOn()
        self.valveB.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ledGreenB.isOn(), True)
        self.assertEqual(self.ledRedB.isOn(), False)

    def test_update_leds_pumpB_on_valveB_on(self):
        self.pumpB.switchOn()
        self.valveB.switchOn()
        self.ctl.updateLeds()
        self.assertEqual(self.ledGreenB.isOn(), False)
        self.assertEqual(self.ledRedB.isOn(), True)

    def test_update_leds_pumpB_off_valveB_off(self):
        self.pumpB.switchOff()
        self.valveB.switchOff()
        self.ctl.updateLeds()
        self.assertEqual(self.ledGreenB.isOn(), False)
        self.assertEqual(self.ledRedB.isOn(), True)

    def test_update_leds_pumpA_off_valveA_off_pumpB_off_valveB_off_cup_true(self):
        self.pumpA.switchOff()
        self.valveA.switchOff()
        self.pumpB.switchOff()
        self.valveB.switchOff()
        self.vesselMix.setPresence(True)
        self.ctl.updateLeds()
        self.assertEqual(self.ledYellowM.isOn(), True)
        self.assertEqual(self.ledGreenM.isOn(), False)

    def test_update_leds_pumpA_off_valveA_off_pumpB_off_valveB_off_cup_false(self):
        self.pumpA.switchOff()
        self.valveA.switchOff()
        self.pumpB.switchOff()
        self.valveB.switchOff()
        self.vesselMix.setPresence(False)
        self.ctl.updateLeds()
        self.assertEqual(self.ledYellowM.isOn(), True)
        self.assertEqual(self.ledGreenM.isOn(), False)

    def test_update_leds_pumpA_on_valveA_off_pumpB_on_valveB_off_cup_false(self):
        self.pumpA.switchOn()
        self.valveA.switchOff()
        self.pumpB.switchOn()
        self.valveB.switchOff()
        self.vesselMix.setPresence(False)
        self.ctl.updateLeds()

        self.assertEqual(self.ledYellowM.isOn(), True)
        self.assertEqual(self.ledGreenM.isOn(), False)

    def test_update_leds_pumpA_on_valveA_off_pumpB_on_valveB_off_cup_true(self):
        self.pumpA.switchOn()
        self.valveA.switchOff()
        self.pumpB.switchOn()
        self.valveB.switchOff()
        self.vesselMix.setPresence(True)
        updateSim(self.sim)
        self.ctl.updateLeds()

        self.assertEqual(self.ledYellowM.isOn(), False)
        self.assertEqual(self.ledGreenM.isOn(), True)

    def test_update_leds_pumpA_on_valveA_on_pumpB_on_valveB_on_cup_true(self):
        self.pumpA.switchOn()
        self.valveA.switchOn()
        self.pumpB.switchOn()
        self.valveB.switchOn()
        self.vesselMix.setPresence(True)
        self.ctl.updateLeds()

        self.assertEqual(self.ledYellowM.isOn(), True)
        self.assertEqual(self.ledGreenM.isOn(), False)

    def test_update_leds_pumpA_on_valveA_on_pumpB_on_valveB_on_cup_false(self):
        self.pumpA.switchOn()
        self.valveA.switchOn()
        self.pumpB.switchOn()
        self.valveB.switchOn()
        self.vesselMix.setPresence(False)
        self.ctl.updateLeds()

        self.assertEqual(self.ledYellowM.isOn(), True)
        self.assertEqual(self.ledGreenM.isOn(), False)

    def test_shutfluids_pumpA_on_pumpB_on(self):
        self.pumpA.switchOn()
        self.pumpB.switchOn()
        self.ctl.shutFluid()
        self.assertEqual(self.pumpA.isOn(), False)
        self.assertEqual(self.pumpB.isOn(), False)
        self.assertEqual(self.valveA.isOn(), True)
        self.assertEqual(self.valveB.isOn(), True)

    def test_validate_cup_appearance_cup_true(self):
        self.vesselMix.setPresence(True)
        updateSim(self.sim)
        self.assertEqual(self.ctl.validateCupAppearance(), True)
        self.assertEqual(self.ctl.fault, CustomController.Faults.NONE)

    def test_validate_cup_appearance_cup_false(self):
        self.vesselMix.setPresence(False)
        self.assertEqual(self.ctl.validateCupAppearance(), False)
        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_CUP_REMOVED)

    def test_syrup_false_water_true(self):
        self.pumpA.switchOn()
        self.pumpB.switchOn()
        self.ctl.liquidLevelSyrup = 0
        self.ctl.liquidLevelWater = 1000
        updateSim(self.sim)
        updateSim(self.sim)

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_SYRUP_SHORTAGE)

    def test_syrup_true_water_false(self):
        self.pumpA.switchOn()
        self.pumpB.switchOn()
        self.ctl.liquidLevelSyrup = 1000
        self.ctl.liquidLevelWater = 0
        updateSim(self.sim)
        updateSim(self.sim)

        self.assertEqual(self.ctl.fault, CustomController.Faults.DISPENSING_WATER_SHORTAGE)
