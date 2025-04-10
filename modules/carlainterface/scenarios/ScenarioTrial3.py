from tools.carlaimporter import carla
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
import pandas as pd
from .scenario import Scenario


class ScenarioTrial3(Scenario):
    def __init__(self):
        super().__init__()
        # Load waypoints and trigger boxes for this trial
        self.identifier = "trial_3"
        self.trajectory_path = "modules/carlainterface/carlainterface_agentclasses/trajectories/trajectory3.csv"  # Load predefined waypoints
        self.scenario_loaded = False
    @property
    def name(self):
        return "Trial 3"

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        """
        This function checks the vehicle's position and triggers actions
        based on its interaction with waypoints and trigger boxes.
        """
        if not self.scenario_loaded:
            carla_interface_process.agent_objects['My Vehicle_1'].load_scenario_data(self.identifier,
                                                                                     self.trajectory_path)
            self.scenario_loaded = True
        if carla_interface_process.agent_objects['My Vehicle_1'].spawned_vehicle is not None:
            # Check final position trigger manually here
            vehicle = carla_interface_process.agent_objects['My Vehicle_1']
            vehicle_location = vehicle.spawned_vehicle.get_location()
            final_location = carla.Location(x=131.10570312, y=-217.95554688, z=1.05)
            distance = vehicle_location.distance(final_location)

            if distance < 5.0:  # Allow some leeway
                print("✅ Trial 3 complete, stopping modules")
                vehicle.destroy()
                carla_interface_process.pipe_comm.send({"stop_all_modules": True})

