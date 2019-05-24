import Controller
import SimulatorInterface
import Effector

import re
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

class TestBaseClass(TestCase):
	def test_can_create(self):
		# Arrange
		object = Mock()
		controller = Mock()

		# Act
		instance = SimulatorInterface.BaseClass(object, controller)

		# Assert
		self.assertIs(object, instance.object)
		self.assertIs(controller, instance.controller)

	def test_update_calls_update_on_object(self):
		# Arrange
		object = Mock()
		controller = Mock()
		target = SimulatorInterface.BaseClass(object, controller)

		# Act
		target.update()

		# Assert
		object.update.assert_called_once()
		
class TestEffector(TestCase):
	def test_can_create(self):
		# Arrange
		objectId = 'objId'
		object = Mock()
		controller = Mock()
		controller._Controller__effectors = { objectId: object }

		# Act
		instance = SimulatorInterface.Effector(controller, objectId)

		# Assert
		self.assertIs(object, instance.object)
		self.assertIs(controller, instance.controller)

	def test_switchOn_calls_switchOn_on_object(self):
		# Arrange
		objectId = 'objId'
		object = Mock()
		controller = Mock()
		controller._Controller__effectors = { objectId: object }
		target = SimulatorInterface.Effector(controller, objectId)

		# Act
		target.switchOn()

		# Assert
		object.switchOn.assert_called_once()

	def test_switchOn_calls_switchOff_on_object(self):
		# Arrange
		objectId = 'objId'
		object = Mock()
		controller = Mock()
		controller._Controller__effectors = { objectId: object }
		target = SimulatorInterface.Effector(controller, objectId)

		# Act
		target.switchOff()

		# Assert
		object.switchOff.assert_called_once()

	def test_isOn_calls_isOn_on_object_and_returns_value(self):
		# Arrange
		isOnValue = True
		objectId = 'objId'
		object = Mock()
		object.isOn = Mock(return_value=isOnValue)
		controller = Mock()
		controller._Controller__effectors = { objectId: object }
		target = SimulatorInterface.Effector(controller, objectId)

		# Act
		result = target.isOn()

		# Assert
		object.isOn.assert_called_once()
		self.assertEqual(result, True)

class TestLED(TestCase):
	def test_can_create(self):
		# Arrange
		objectId = 'objId'
		object = Mock()
		controller = Mock()
		controller._Controller__effectors = { objectId: object }

		# Act
		instance = SimulatorInterface.LED(controller, objectId)

		# Assert
		self.assertIs(object, instance.object)
		self.assertIs(controller, instance.controller)

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