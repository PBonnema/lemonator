# pylint: disable=no-self-use, missing-docstring
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch, call

import Simulator
import CustomController as Controller

from SimulatorInterface import SimulatorInterface

class TestEffector(TestCase):
    def test_can_create(self):
        # Arrange
        obj = Mock(spec_set=[''])

        # Act
        instance = SimulatorInterface.Effector(obj)

        # Assert
        self.assertIs(obj, instance.object)

    def test_switchOn_calls_switchOn_on_object(self):
        # Arrange
        obj = Mock(spec_set=['switchOn'])
        target = SimulatorInterface.Effector(obj)

        # Act
        target.switchOn()

        # Assert
        obj.switchOn.assert_called_once()

    def test_switchOff_calls_switchOff_on_object(self):
        # Arrange
        obj = Mock(spec_set=['switchOff'])
        target = SimulatorInterface.Effector(obj)

        # Act
        target.switchOff()

        # Assert
        obj.switchOff.assert_called_once()

    def test_isOn_calls_isOn_on_object_and_returns_value(self):
        # Arrange
        isOnValue = True
        obj = Mock(spec_set=['isOn'])
        obj.isOn.return_value = isOnValue
        target = SimulatorInterface.Effector(obj)

        # Act
        result = target.isOn()

        # Assert
        obj.isOn.assert_called_once()
        self.assertEqual(result, True)

class TestLED(TestCase):
    def test_can_create(self):
        # Arrange
        obj = Mock(spec_set=[''])

        # Act
        instance = SimulatorInterface.LED(obj)

        # Assert
        self.assertIs(obj, instance.object)

    def test_toggle_toggles_the_object(self):
        # Arrange
        obj = Mock(spec_set=['toggle'])
        target = SimulatorInterface.LED(obj)

        # Act
        target.toggle()

        # Assert
        obj.toggle.assert_called_once()

class TestLCD(TestCase):
    def test_can_create(self):
        # Arrange
        obj = Mock(spec_set=[''])

        # Act
        instance = SimulatorInterface.LCD(obj)

        # Assert
        self.assertIs(obj, instance.object)

    def test_pushString_pushes_the_string_to_the_object(self):
        # Arrange
        string = 'manylines\nevenmorelines\n'
        obj = Mock(spec_set=['pushString'])
        target = SimulatorInterface.LCD(obj)

        # Act
        target.pushString(string)

        # Assert
        obj.pushString.assert_called_once_with('manylines\nevenmorelines\n')

    def test_clear_clears_the_object(self):
        # Arrange
        obj = Mock(spec_set=['clear'])
        target = SimulatorInterface.LCD(obj)

        # Act
        target.clear()

        # Assert
        obj.clear.assert_called_once()

    def test_putc_puts_the_character_in_the_object(self):
        # Arrange
        char = 'a'
        obj = Mock(spec_set=['put'])
        target = SimulatorInterface.LCD(obj)

        # Act
        target.putc(char)

        # Assert
        obj.put.assert_called_once_with('a')

class TestSensor(TestCase):
    def test_can_create(self):
        # Arrange
        obj = Mock(spec_set=[''])

        # Act
        instance = SimulatorInterface.Sensor(obj)

        # Assert
        self.assertIs(obj, instance.object)

    def test_readValue_reads_and_returns_the_current_value(self):
        # Arrange
        value = 5.1
        obj = Mock(spec_set=['readValue'])
        obj.readValue.return_value = value
        target = SimulatorInterface.Sensor(obj)

        # Act
        result = target.readValue()

        # Assert
        obj.readValue.assert_called_once()
        self.assertEqual(result, 5.1)

class TestPresenceSensor(TestCase):
    def test_can_create(self):
        # Arrange
        obj = Mock(spec_set=[''])

        # Act
        instance = SimulatorInterface.PresenceSensor(obj)

        # Assert
        self.assertIs(obj, instance.object)

    def test_readValue_reads_and_returns_the_current_value(self):
        # Arrange
        value = False
        obj = Mock(spec_set=['readValue'])
        obj.readValue.return_value = value
        target = SimulatorInterface.PresenceSensor(obj)

        # Act
        result = target.readValue()

        # Assert
        obj.readValue.assert_called_once()
        self.assertEqual(result, False)

class TestKeypad(TestCase):
    def test_can_create(self):
        # Arrange
        obj = Mock(spec_set=[''])

        # Act
        instance = SimulatorInterface.Keypad(obj)

        # Assert
        self.assertIs(obj, instance.object)

    def test_pop_pops_the_next_character(self):
        # Arrange
        obj = Mock(spec_set=['pop'])
        target = SimulatorInterface.Keypad(obj)

        # Act
        target.pop()

        # Assert
        obj.pop.assert_called_once()

    def test_popAll_returns_empty_string_if_only_char_is_null_char(self):
        # Arrange
        obj = Mock(spec_set=['pop'])
        obj.pop.return_value = '\x00'
        target = SimulatorInterface.Keypad(obj)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, '')

    def test_popAll_returns_all_chars_before_null_char(self):
        # Arrange
        obj = Mock(spec_set=['pop'])
        obj.pop.side_effect = 'abc\x00'
        target = SimulatorInterface.Keypad(obj)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, 'abc')

    def test_popAll_ignores_all_after_first_null_char(self):
        # Arrange
        obj = Mock(spec_set=['pop'])
        obj.pop.side_effect = 'a\x00abc\x00'
        target = SimulatorInterface.Keypad(obj)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, 'a')

    def test_popAll_returns_empty_string_if_first_char_is_null_char(self):
        # Arrange
        obj = Mock(spec_set=['pop'])
        obj.pop.side_effect = '\x00abc'
        target = SimulatorInterface.Keypad(obj)

        # Act
        result = target.popAll()

        # Assert
        self.assertEqual(result, '')
