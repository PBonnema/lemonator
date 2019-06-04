# pylint: disable=no-self-use, missing-docstring
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch, call

import Simulator
import Controller

from SimulatorInterface import SimulatorInterface

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
        obj.isOn.return_value = isOnValue
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

        # Act
        instance = SimulatorInterface.LED(controller, objectId)

        # Assert
        self.assertIs(obj, instance.object)
        self.assertIs(controller, instance.controller)

    def test_toggle_toggles_the_object(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['toggle'])
        controller = Mock(spec_set=['_Controller__effectors'])
        controller._Controller__effectors = {objectId: obj}
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
        obj.getColour.return_value = colour
        controller = Mock(spec_set=['_Controller__effectors'])
        controller._Controller__effectors = {objectId: obj}
        target = SimulatorInterface.LED(controller, objectId)

        # Act
        result = target.getColour()

        # Assert
        obj.getColour.assert_called_once()
        self.assertEqual(True, result)

class TestLCD(TestCase):
    def test_can_create(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=[''])
        controller = Mock(spec_set=['_Controller__effectors'])
        controller._Controller__effectors = {objectId: obj}

        # Act
        instance = SimulatorInterface.LCD(controller, objectId)

        # Assert
        self.assertIs(obj, instance.object)
        self.assertIs(controller, instance.controller)

    def test_getLines_returns_the_lines_of_the_object(self):
        # Arrange
        lines = 'manylines\nevenmorelines\n'
        objectId = 'objId'
        obj = Mock(spec_set=['getLines'])
        obj.getLines.return_value = lines
        controller = Mock(spec_set=['_Controller__effectors'])
        controller._Controller__effectors = {objectId: obj}
        target = SimulatorInterface.LCD(controller, objectId)

        # Act
        result = target.getLines()

        # Assert
        obj.getLines.assert_called_once()
        self.assertEqual(result, 'manylines\nevenmorelines\n')

    def test_pushString_pushes_the_string_to_the_object(self):
        # Arrange
        string = 'manylines\nevenmorelines\n'
        objectId = 'objId'
        obj = Mock(spec_set=['pushString'])
        controller = Mock(spec_set=['_Controller__effectors'])
        controller._Controller__effectors = {objectId: obj}
        target = SimulatorInterface.LCD(controller, objectId)

        # Act
        target.pushString(string)

        # Assert
        obj.pushString.assert_called_once_with('manylines\nevenmorelines\n')

    def test_clear_clears_the_object(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['clear'])
        controller = Mock(spec_set=['_Controller__effectors'])
        controller._Controller__effectors = {objectId: obj}
        target = SimulatorInterface.LCD(controller, objectId)

        # Act
        target.clear()

        # Assert
        obj.clear.assert_called_once()

    def test_putc_puts_the_character_in_the_object(self):
        # Arrange
        char = 'a'
        objectId = 'objId'
        obj = Mock(spec_set=['put'])
        controller = Mock(spec_set=['_Controller__effectors'])
        controller._Controller__effectors = {objectId: obj}
        target = SimulatorInterface.LCD(controller, objectId)

        # Act
        target.putc(char)

        # Assert
        obj.put.assert_called_once_with('a')

class TestSensor(TestCase):
    def test_can_create(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=[''])
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}

        # Act
        instance = SimulatorInterface.Sensor(controller, objectId)

        # Assert
        self.assertIs(obj, instance.object)
        self.assertIs(controller, instance.controller)

    def test_readValue_reads_and_returns_the_current_value(self):
        # Arrange
        value = 5.1
        objectId = 'objId'
        obj = Mock(spec_set=['readValue'])
        obj.readValue.return_value = value
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Sensor(controller, objectId)

        # Act
        result = target.readValue()

        # Assert
        obj.readValue.assert_called_once()
        self.assertEqual(result, 5.1)

    def test_measure_reads_and_returns_the_current_value_with_unit(self):
        # Arrange
        value = '5.1 ml'
        objectId = 'objId'
        obj = Mock(spec_set=['readValue'])
        obj.readValue.return_value = value
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Sensor(controller, objectId)

        # Act
        result = target.readValue()

        # Assert
        obj.readValue.assert_called_once()
        self.assertEqual(result, '5.1 ml')

class TestPresenceSensor(TestCase):
    def test_can_create(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=[''])
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}

        # Act
        instance = SimulatorInterface.PresenceSensor(controller, objectId)

        # Assert
        self.assertIs(obj, instance.object)
        self.assertIs(controller, instance.controller)

    def test_readValue_reads_and_returns_the_current_value(self):
        # Arrange
        value = False
        objectId = 'objId'
        obj = Mock(spec_set=['readValue'])
        obj.readValue.return_value = value
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.PresenceSensor(controller, objectId)

        # Act
        result = target.readValue()

        # Assert
        obj.readValue.assert_called_once()
        self.assertEqual(result, False)

class TestKeypad(TestCase):
    def test_can_create(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=[''])
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}

        # Act
        instance = SimulatorInterface.Keypad(controller, objectId)

        # Assert
        self.assertIs(obj, instance.object)
        self.assertIs(controller, instance.controller)

    def test_push_pushes_the_character(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['push'])
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)
        char = 'a'

        # Act
        target.push(char)

        # Assert
        obj.push.assert_called_once_with('a')

    def test_pop_pops_the_next_character(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['pop'])
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)

        # Act
        target.pop()

        # Assert
        obj.pop.assert_called_once()

    def test_pushString_does_nothing_with_empty_string(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['push'])
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
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
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)
        string = 'ab12'

        # Act
        target.pushString(string)

        # Assert
        self.assertListEqual(obj.push.mock_calls, [
            call('a'), call('b'), call('1'), call('2')
        ])

    def test_popAll_returns_empty_string_if_only_char_is_null_char(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['pop'])
        obj.pop.return_value = '\x00'
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, '')

    def test_popAll_returns_all_chars_before_null_char(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['pop'])
        obj.pop.side_effect = 'abc\x00'
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, 'abc')

    def test_popAll_ignores_all_after_first_null_char(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['pop'])
        obj.pop.side_effect = 'a\x00abc\x00'
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, 'a')

    def test_popAll_returns_empty_string_if_first_char_is_null_char(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['pop'])
        obj.pop.side_effect = '\x00abc'
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, '')

    def test_readBuffer_pushes_pipe_char_then_returns_empty_string_if_popped_char_is_a_pipe(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['push', 'pop'])
        obj.pop.return_value = '|'
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)

        # Act
        result = target.readBuffer()

        # Assert
        obj.push.assert_called_once_with('|')
        obj.pop.assert_called_once()
        self.assertEqual(result, '')

    def test_readBuffer_pushes_pipe_char_then_pushes_what_it_pops(self):
        # Arrange
        objectId = 'objId'
        obj = Mock(spec_set=['push', 'pop'])
        obj.pop.side_effect = 'abcd|'
        controller = Mock(spec_set=['_Controller__sensors'])
        controller._Controller__sensors = {objectId: obj}
        target = SimulatorInterface.Keypad(controller, objectId)

        # Act
        result = target.readBuffer()

        # Assert
        self.assertListEqual(obj.pop.mock_calls, [
            call(), call(), call(), call(), call()
        ])
        self.assertListEqual(obj.push.mock_calls, [
            call('|'), call('a'), call('b'), call('c'), call('d')
        ])
        self.assertEqual(result, 'abcd')

class TestSimulatorControlFactory(TestCase):
    class BaseClassMagicMock(MagicMock):
        def __subclasscheck__(self, subclass):
            return self is subclass

    @patch('SimulatorInterface.SimulatorInterface.BaseClass', new_callable=BaseClassMagicMock)
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

    @patch('SimulatorInterface.SimulatorInterface.BaseClass', new_callable=BaseClassMagicMock)
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

    @patch('SimulatorInterface.SimulatorInterface.BaseClass', new_callable=AnotherClassMagicMock)
    def test_create_invalid_instance(self, MockClass):
        # Arrange
        createdInstance = Mock(spec_set=[''])
        MockClass.return_value = createdInstance
        MockClass.__name__ = 'AnotherClass'
        controller = Mock(spec_set=[''])
        target = SimulatorInterface.Factory(controller)

        # Act
        def action():
            target.make(MockClass)

        # Assert
        with self.assertRaises(TypeError) as cm:
            action()
        self.assertEqual(str(cm.exception), 'Class instance AnotherClass does not have a valid base class.')
