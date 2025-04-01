from tools.carlaimporter import carla
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
import pandas as pd
from .scenario import Scenario


class ScenarioTrial1(Scenario):
    def __init__(self):
        super().__init__()
        # Load waypoints and trigger boxes for this trial

        ####MAYBE SEND THIS THROUGH TO THE FUNCTION OF THE VEHICLE
        self.identifier = "trial_1"
        self.trajectory_path = "modules/carlainterface/carlainterface_agentclasses/trajectories/trajectory1.csv"  # Load predefined waypoints
        self.scenario_loaded = False
    @property
    def name(self):
        return "Trial 1"

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        """
        This function checks the vehicle's position and triggers actions
        based on its interaction with waypoints and trigger boxes.
        """
        if not self.scenario_loaded:
            carla_interface_process.agent_objects['My Vehicle_1'].load_scenario_data(self.identifier, self.trajectory_path)
            self.scenario_loaded = True
