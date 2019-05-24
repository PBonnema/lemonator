import Simulator
import SimulatorControl
import Effector
import unittest

class TestSimulatorControlFactory(unittest.TestCase):
	def test_create_valid_simulator_control_instance(self):
		sim = Simulator.Simulator(False)
		factory = SimulatorControl.Factory(sim)
		VesselA = factory.make(SimulatorControl.Vessel, 'a')
		self.assertTrue(isinstance(VesselA, SimulatorControl.Vessel))

	def test_create_invalid_simulator_control_instance(self):
		sim = Simulator.Simulator(False)

		class TempClass:
			pass

		factory = SimulatorControl.Factory(sim)

		with self.assertRaises(TypeError):
			factory.make(TempClass, 'a')
			

		'''
	 	self.assertEqual(controller.PumpA.isOn(), False)
	 	self.assertEqual(controller.PumpB.isOn(), False)
	 	self.assertEqual(controller.ValveA.isOn(), True)
	 	self.assertEqual(controller.ValveB.isOn(), True)
	 	self.assertEqual(controller.Heater.isOn(), False)

	 	self.assertEqual(controller.LedRedA.isOn(), True)
	 	self.assertEqual(controller.LedGreenA.isOn(), False)
	 	self.assertEqual(controller.LedRedB.isOn(),	True)
	 	self.assertEqual(controller.LedGreenB.isOn(), False)
	 	self.assertEqual(controller.LedGreenM.isOn(), False)
	 	self.assertEqual(controller.LedYellowM.isOn(), True)
		'''

			
