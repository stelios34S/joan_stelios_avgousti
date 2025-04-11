from tools.carlaimporter import carla
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
import pandas as pd
from .scenario import Scenario


class ScenarioTrial2(Scenario):
    def __init__(self):
        super().__init__()
        # Load waypoints and trigger boxes for this trial
        self.identifier = "trial_2"
        self.trajectory_path = "modules/carlainterface/carlainterface_agentclasses/trajectories/trajectory2.csv"  # Load predefined waypoints
        self.scenario_loaded = False
        self.cruisecontrolflag = False
    @property
    def name(self):
        return "Trial 2"

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
            final_location = carla.Location(x=329.82621094, y=-182.390625, z=1.05)
            distance = vehicle_location.distance(final_location)

            if distance < 5.0:  # Allow some leeway
                print("✅ Trial 2 complete, stopping modules")
                vehicle.destroy()
                carla_interface_process.pipe_comm.send({"stop_all_modules": True})

            if carla_interface_process.agent_objects['Ego Vehicle_1'].spawned_vehicle is not None:
                bike = carla_interface_process.agent_objects['Ego Vehicle_1']
                bikeloc = bike.spawned_vehicle.get_location()
                checkloc = carla.Location(x=200.44917969, y=-252.10375, z=1.05)
                destroyloc = carla.Location(x=191.08195312, y=-248.87417969,z=1.05)
                if vehicle_location.distance(checkloc) < 5 and not self.cruisecontrolflag:
                    self.cruisecontrolflag = True
                    bike.settings.set_velocity = True
                    bike.settings.velocity = 15
                if bikeloc.distance(destroyloc) < 4 :
                    self.cruisecontrolflag = False
                    bike.destroy()
            if carla_interface_process.agent_objects['Ego Vehicle_2'].spawned_vehicle is not None:
                bike = carla_interface_process.agent_objects['Ego Vehicle_2']
                bikeloc = bike.spawned_vehicle.get_location()
                checkloc = carla.Location(x=202.105, y=-351.22683594, z=1.05)
                destroyloc = carla.Location(x=238.40304688, y=-307.14478516,z=1.05)
                if vehicle_location.distance(checkloc) < 5 and not self.cruisecontrolflag:
                    self.cruisecontrolflag = True
                    bike.settings.set_velocity = True
                    bike.settings.velocity = 25
                if bikeloc.distance(destroyloc) < 4 :
                    self.cruisecontrolflag = False
                    bike.destroy()