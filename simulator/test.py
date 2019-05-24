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

	unittest.main()
