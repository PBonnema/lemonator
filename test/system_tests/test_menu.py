# pylint: disable=no-self-use, missing-docstring
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call, patch
# from threading import Thread
import asyncio

import Constants
import CustomController
import Simulator
import SimulatorInterface

# For now, we only test the pumps, valves, displays, keypad and the heater. LED's are out of scope for now...

def updateSim(simulator):
    simulator._Simulator__plant.update()
    simulator._Simulator__controller.update()
    simulator._Simulator__monitor.update()

class TestMenu(TestCase):
    def setUp(self):
        self.sim = Simulator.Simulator(False)
        self.ctl = CustomController.Controller(
            self.sim._Simulator__plant._sensors,
            self.sim._Simulator__plant._effectors,
            SimulatorInterface.SimulatorInterface
        )
        self.sim._Simulator__controller = self.ctl

        # These variables are there for convenience
        self.LCD = self.sim._Simulator__plant._effectors['lcd']

    def test_main_menu_header_is_correct(self):
        self.assertEqual(self.LCD.getLines(), '\x0c   Lemonator v1.0\n--------------------\n')

    def test_main_menu_header_is_correct2(self):
        self.assertEqual(self.LCD.getLines(), '\x0c   Lemonator v1.0\n--------------------\n')
