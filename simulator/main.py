import Simulator
import SimulatorInterface
import Controller

if __name__ == "__main__":

    simulator = Simulator.Simulator(True)
    
    simulator._Simulator__controller = Controller.Controller(simulator._Simulator__plant._sensors, simulator._Simulator__plant._effectors, SimulatorInterface.SimulatorInterface)

    simulator.run()


