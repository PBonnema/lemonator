import Controller
import SimulatorInterface
import Effector

import re
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

class TestSimulatorControlFactory(TestCase):
	class BaseClassMagicMock(MagicMock):
		def __subclasscheck__(self, subclass):
			return self is subclass
			
	@patch('SimulatorInterface.BaseClass', new_callable=BaseClassMagicMock)
	def test_create_valid_instance(self, MockClass):
		# Arrange
		createdInstance = Mock()
		MockClass.return_value = createdInstance
		controller = Mock()
		target = SimulatorInterface.Factory(controller)

		# Act
		dummy = target.make(MockClass)

		# Assert
		MockClass.assert_called_once_with(controller)
		self.assertIs(createdInstance, dummy)

	@patch('SimulatorInterface.BaseClass', new_callable=BaseClassMagicMock)
	def test_create_instance_with_arguments(self, MockClass):
		# Arrange
		createdInstance = Mock()
		MockClass.return_value = createdInstance
		controller = Mock()
		target = SimulatorInterface.Factory(controller)

		# Act
		dummy = target.make(MockClass, 1, 2, 'a')

		# Assert
		MockClass.assert_called_once_with(controller, 1, 2, 'a')
		self.assertIs(createdInstance, dummy)

	class AnotherClassMagicMock(MagicMock):
		def __subclasscheck__(self, subclass):
			return False

	@patch('SimulatorInterface.BaseClass', new_callable=AnotherClassMagicMock)
	def test_create_invalid_instance(self, MockClass):
		# Arrange
		createdInstance = Mock()
		MockClass.return_value = createdInstance
		MockClass.__name__ = 'AnotherClass'
		controller = Mock()
		target = SimulatorInterface.Factory(controller)

		# Act
		def action(): target.make(MockClass)

		# Assert
		with self.assertRaises(TypeError) as cm:
			action()
		self.assertEqual(str(cm.exception), 'Class instance AnotherClass does not have a valid base class.')

		
	 	# self.assertEqual(controller.PumpA.isOn(), False)
	 	# self.assertEqual(controller.PumpB.isOn(), False)
	 	# self.assertEqual(controller.ValveA.isOn(), True)
	 	# self.assertEqual(controller.ValveB.isOn(), True)
	 	# self.assertEqual(controller.Heater.isOn(), False)

	 	# self.assertEqual(controller.LedRedA.isOn(), True)
	 	# self.assertEqual(controller.LedGreenA.isOn(), False)
	 	# self.assertEqual(controller.LedRedB.isOn(),	True)
	 	# self.assertEqual(controller.LedGreenB.isOn(), False)
	 	# self.assertEqual(controller.LedGreenM.isOn(), False)
	 	# self.assertEqual(controller.LedYellowM.isOn(), True)