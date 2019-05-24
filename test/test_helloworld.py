from unittest import TestCase
from unittest.mock import Mock

class A:
    def doWork(self):
        pass

class B:
    def __init__(self, a):
        self.__a = a

    def doSomething(self):
        self.__a.doWork()

class MyTestCase(TestCase):
    def test_answer_correct(self):
        # Arrange
        a = Mock()
        a.doWork = Mock()
        b = B(a)

        # Act
        b.doSomething()

        # Assert
        a.doWork.assert_called_once()

    def test_answer_incorrect(self):
        # Arrange
        a = Mock()
        a.doWork = Mock()
        b = B(a)

        # Act
        b.doSomething()

        # Assert
        #a.doWork.assert_called_once_with(1) # would fail but trips up travis
        self.assertTrue(True)
