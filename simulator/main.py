import Simulator
import SimulatorInterface
import CustomController
import Gui

if __name__ == "__main__":
    
    # A bit of explaining here is needed, because I want to overwrite the GUI with our custom controller. 
    # You don't want the simulator to make the GUI for you. So the GUI bool is set to False.
    simulator = Simulator.Simulator(False)

    # Here is the simulator assigned
    Interface = SimulatorInterface.SimulatorInterface
    
    # Here is the Controller created with a custom interface, here you can use a SoftwareInterface or a HardwareInterface
    controllerObject = CustomController.Controller(simulator._Simulator__plant._sensors, simulator._Simulator__plant._effectors, Interface)
    
    # Here is the GUI created. This is the GUI, that the simulator will use. Thereby it uses our custom controller.
    simulator._Simulator__gui = Gui.GUI(simulator._Simulator__plant, controllerObject, simulator._Simulator__monitor)

    # The GUI still has to be actived by the simulator. 
    simulator.run()


