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
        self.trajectory_path = "modules/carlainterface/carlainterface_agentclasses/trajectories/trajectory1new.csv"  # Load predefined waypoints
        self.scenario_loaded = False
        self.cruisecontrolflag = False

    @property
    def name(self):
        return "Trial 1"

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        """
        This function checks the vehicle's position and triggers actions
        based on its interaction with waypoints and trigger boxes.
        """
        if not self.scenario_loaded:
            carla_interface_process.agent_objects['My Vehicle_1'].load_scenario_data(self.identifier,
                                                                                     self.trajectory_path)
            self.scenario_loaded = True

        # Check final position trigger manually here
        if carla_interface_process.agent_objects['My Vehicle_1'].spawned_vehicle is not None:
            vehicle = carla_interface_process.agent_objects['My Vehicle_1']
            vehicle_location = vehicle.spawned_vehicle.get_location()
            final_location = carla.Location(x=295.42828125, y=-223.13464844, z=1.05)
            #final_location = carla.Location(x=13.04862549, y=-209.53740234, z=1.05)
            distance = vehicle_location.distance(final_location)
            if distance < 5.0:  # Allow some leeway
                print("✅ Trial 1 complete, stopping modules")
                vehicle.destroy()
                carla_interface_process.pipe_comm.send({"stop_all_modules": True})

            if carla_interface_process.agent_objects['Ego Vehicle_1'].spawned_vehicle is not None:
                bike = carla_interface_process.agent_objects['Ego Vehicle_1']
                bikeloc = bike.spawned_vehicle.get_location()
                checkloc = carla.Location(x=348.0753125, y=-131.11517578, z=1.05)
                destroyloc = carla.Location(x=316.40402344, y=-173.16640625, z=1.05)
                if vehicle_location.distance(checkloc) < 4 and not self.cruisecontrolflag:
                    self.cruisecontrolflag = True
                    bike.settings.set_velocity = True
                    bike.settings.velocity = 15
                if bikeloc.distance(destroyloc) < 4:
                    self.cruisecontrolflag = False
                    bike.destroy()