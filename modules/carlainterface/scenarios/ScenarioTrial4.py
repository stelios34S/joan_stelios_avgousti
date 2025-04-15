from tools.carlaimporter import carla
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
import pandas as pd
from .scenario import Scenario


class ScenarioTrial3(Scenario):
    def __init__(self):
        super().__init__()
        # Load waypoints and trigger boxes for this trial
        self.identifier = "trial_4"
        self.trajectory_path = "modules/carlainterface/carlainterface_agentclasses/trajectories/trajectory4.csv"  # Load predefined waypoints
        self.scenario_loaded = False
        self.cruisecontrolflag = False
    @property
    def name(self):
        return "Trial 4"

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

            if carla_interface_process.agent_objects['Ego Vehicle_1'].spawned_vehicle is not None:
                bike = carla_interface_process.agent_objects['Ego Vehicle_1']
                bikeloc = bike.spawned_vehicle.get_location()
                checkloc = carla.Location(x=251.75382812, y=-307.34134766, z=1.05)
                destroyloc = carla.Location(x=259.50169922, y=-307.10992188,z=1.05)
                if vehicle_location.distance(checkloc) < 5 and not self.cruisecontrolflag:
                    self.cruisecontrolflag = True
                    bike.settings.set_velocity = True
                    bike.settings.velocity = 14
                if bikeloc.distance(destroyloc) < 4 :
                    self.cruisecontrolflag = False
                    bike.destroy()
            if carla_interface_process.agent_objects['Ego Vehicle_2'].spawned_vehicle is not None:
                bike = carla_interface_process.agent_objects['Ego Vehicle_2']
                bikeloc = bike.spawned_vehicle.get_location()
                checkloc = carla.Location(x=202.96996094, y=-181.60287109, z=1.05)
                destroyloc = carla.Location(x=199.13095703, y=-157.41007812, z=1.05)
                if vehicle_location.distance(checkloc) < 5 and not self.cruisecontrolflag:
                    self.cruisecontrolflag = True
                    bike.settings.set_velocity = True
                    bike.settings.velocity = 25
                if bikeloc.distance(destroyloc) < 4:
                    self.cruisecontrolflag = False
                    bike.destroy()
            if carla_interface_process.agent_objects['Ego Vehicle_3'].spawned_vehicle is not None:
                bike = carla_interface_process.agent_objects['Ego Vehicle_3']
                bikeloc = bike.spawned_vehicle.get_location()
                checkloc = carla.Location(x=254.06978516, y=-180.79351562, z=1.05)
                destroyloc = carla.Location(x=303.38798828, y=-168.13054688,z=1.05)
                if vehicle_location.distance(checkloc) < 5 and not self.cruisecontrolflag:
                    self.cruisecontrolflag = True
                    bike.settings.set_velocity = True
                    bike.settings.velocity = 30
                if bikeloc.distance(destroyloc) < 4 :
                    self.cruisecontrolflag = False
                    bike.destroy()