# import Effector

import re
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch, call

# import Simulator
# import Controller
import SimulatorInterface


# sensors = Simulator._Simulator__plant._sensors
# effectors = Simulator._Simulator__plant._effectors


# controller = Controller(sensors, effectors, SimulatorInterface)
# instance = SimulatorInterface.BaseClass(effectors.PumpA, controller)

class TestBaseClass(TestCase):
	def test_can_create(self):
		# Arrange
		obj = Mock(spec_set=[''])
		controller = Mock(spec_set=[''])

		# Act
		instance = SimulatorInterface.BaseClass(obj, controller)

		# Assert
		self.assertIs(obj, instance.object)
		self.assertIs(controller, instance.controller)

	def test_update_calls_update_on_object(self):
		# Arrange
		obj = Mock(spec_set=['update'])
		controller = Mock(spec_set=[''])
		target = SimulatorInterface.BaseClass(obj, controller)

		# Act
		target.update()

		# Assert
		obj.update.assert_called_once()


class TestEffector(TestCase):
	def test_can_create(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=[''])
		controller = Mock(spec_set=['_Controller__effectors'])
		controller._Controller__effectors = {objectId: obj}

		# Act
		instance = SimulatorInterface.Effector(controller, objectId)

		# Assert
		self.assertIs(obj, instance.object)
		self.assertIs(controller, instance.controller)

	def test_switchOn_calls_switchOn_on_object(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=['switchOn'])
		controller = Mock(spec_set=['_Controller__effectors'])
		controller._Controller__effectors = {objectId: obj}
		target = SimulatorInterface.Effector(controller, objectId)

		# Act
		target.switchOn()

		# Assert
		obj.switchOn.assert_called_once()

	def test_switchOn_calls_switchOff_on_object(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=['switchOff'])
		controller = Mock(spec_set=['_Controller__effectors'])
		controller._Controller__effectors = {objectId: obj}
		target = SimulatorInterface.Effector(controller, objectId)

		# Act
		target.switchOff()

		# Assert
		obj.switchOff.assert_called_once()

	def test_isOn_calls_isOn_on_object_and_returns_value(self):
		# Arrange
		isOnValue = True
		objectId = 'objId'
		obj = Mock(spec_set=['isOn'])
		obj.isOn = Mock(return_value=isOnValue)
		controller = Mock(spec_set=['_Controller__effectors'])
		controller._Controller__effectors = {objectId: obj}
		target = SimulatorInterface.Effector(controller, objectId)

		# Act
		result = target.isOn()

		# Assert
		obj.isOn.assert_called_once()
		self.assertEqual(result, True)


class TestLED(TestCase):
	def test_can_create(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=[''])
		controller = Mock(spec_set=['_Controller__effectors'])
		controller._Controller__effectors = {objectId: obj}

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
        self.assertEqual(str(
            cm.exception), 'Class instance AnotherClass does not have a valid base class.')

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


class TestStateMachine(TestCase):
    def test_check_is_enum(self):
        # Arrange
        sm = Controller.States.IDLE

        # Assert
        self.assertIsInstance(sm, Enum)
        self.assertIsNot(len(Controller.States), 0)
        self.assertEqual(sm, Controller.States.IDLE)


"""
class TestControllerLogic(TestCase):

    def setUp(self):
        # Arrange
        self.controller = Mock()

    def test_check_controller_initialisation(self):
        pass

    def test_initial_state(self):
        # controller = Controller.Controller()
        # Assert
        self.assertEqual(self.controller.state, Controller.States.IDLE)

    def test_press_other(self):
        # Assert
        # Nothing should happen to our state here, we only transition when the user has pressed A.
        self.assertEqual(self.controller.state, Controller.States.IDLE)

    def test_press_A(self):
        # Act
        # --> Perform the keypress

        # Assert
        # Check if we transiiton to the next state...
        self.assertEqual(self.controller.state,
                         Controller.States.WAITING_FOR_CUP)

    def test_cup_detection_succeeded(self):
        # Act
        # --> Place the cup.

        self.assertEqual(self.controller.state,
                         Controller.States.WAITING_USER_SELECTION)

    def test_user_ml_selection_liquid_one(self):
        # Test the ml select of liquid one.
        pass

    def test_user_ml_selection_liquid_two(self):
        # Test the ml select of liquid two.
        pass

    def test_user_ml_selection_too_large_amount(self):
        # Select a too large amount of liquid.

        # Assert
        self.assertEqual(self.controller.state, Controller.States.FAULT)

    def test_cup_removed_pour_stop(self):
        # Test if we stop dispensing in the case the cup is removed.
        pass

    def test_dispensing_finished(self):
        # Assert
        self.assertEqual(self.controller.state,
                         Controller.States.DISPENSING_DONE)
"""
		# Assert
		self.assertIs(obj, instance.object)
		self.assertIs(controller, instance.controller)

	def test_toggle_toggles_the_object(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=['toggle'])
		controller = Mock(spec_set=['_Controller__effectors'])
		controller._Controller__effectors = { objectId: obj }
		target = SimulatorInterface.LED(controller, objectId)

		# Act
		target.toggle()

		# Assert
		obj.toggle.assert_called_once()

	def test_getColour_returns_the_objects_colour(self):
		# Arrange
		colour = True
		objectId = 'objId'
		obj = Mock(spec_set=['getColour'])
		obj.getColour = Mock(return_value=colour)
		controller = Mock(spec_set=['_Controller__effectors'])
		controller._Controller__effectors = { objectId: obj }
		target = SimulatorInterface.LED(controller, objectId)

		# Act
		result = target.getColour()

		# Assert
		obj.getColour.assert_called_once()
		self.assertEqual(True, result)
		
class TestKeypad(TestCase):
	def test_can_create(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=[''])
		controller = Mock(spec_set=['_Controller__sensors'])
		controller._Controller__sensors = { objectId: obj }

		# Act
		instance = SimulatorInterface.Keypad(controller, objectId)

		# Assert
		self.assertIs(obj, instance.object)
		self.assertIs(controller, instance.controller)
		
	def test_pushString_does_nothing_with_empty_string(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=['push'])
		controller = Mock(spec_set=['_Controller__sensors'])
		controller._Controller__sensors = { objectId: obj }
		target = SimulatorInterface.Keypad(controller, objectId)
		string = ''

		# Act
		target.pushString(string)

		# Assert
		obj.push.assert_not_called()
		
	def test_pushString_pushes_each_char_of_the_string(self):
		# Arrange
		objectId = 'objId'
		obj = Mock(spec_set=['push'])
		controller = Mock(spec_set=['_Controller__sensors'])
		controller._Controller__sensors = { objectId: obj }
		target = SimulatorInterface.Keypad(controller, objectId)
		string = 'ab12'

		# Act
		target.pushString(string)

		# Assert
		self.assertListEqual(obj.push.mock_calls, [call('a'), call('b'), call('1'), call('2')])

class TestSimulatorControlFactory(TestCase):
	class BaseClassMagicMock(MagicMock):
		def __subclasscheck__(self, subclass):
			return self is subclass
			
	@patch('SimulatorInterface.BaseClass', new_callable=BaseClassMagicMock)
	def test_create_valid_instance(self, MockClass):
		# Arrange
		createdInstance = Mock(spec_set=[''])
		MockClass.return_value = createdInstance
		controller = Mock(spec_set=[''])
		target = SimulatorInterface.Factory(controller)

		# Act
		dummy = target.make(MockClass)

		# Assert
		MockClass.assert_called_once_with(controller)
		self.assertIs(createdInstance, dummy)

	@patch('SimulatorInterface.BaseClass', new_callable=BaseClassMagicMock)
	def test_create_instance_with_arguments(self, MockClass):
		# Arrange
		createdInstance = Mock(spec_set=[''])
		MockClass.return_value = createdInstance
		controller = Mock(spec_set=[''])
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
		createdInstance = Mock(spec_set=[''])
		MockClass.return_value = createdInstance
		MockClass.__name__ = 'AnotherClass'
		controller = Mock(spec_set=[''])
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
