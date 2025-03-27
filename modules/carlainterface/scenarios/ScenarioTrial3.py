from tools.carlaimporter import carla
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess
import pandas as pd
from .scenario import Scenario


class ScenarioTrial3(Scenario):
    def __init__(self):
        super().__init__()
        # Load waypoints and trigger boxes for this trial
        self.waypoints = self.define_manual_waypoints(
            "modules/carlainterface/carlainterface_agentclasses/trajectories/trajectory3.csv")  # Load predefined waypoints
        self.trigger_boxes = self.load_trigger_boxes()  # Load predefined trigger boxes

    @property
    def name(self):
        return "Trial 3"

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        """
        This function checks the vehicle's position and triggers actions
        based on its interaction with waypoints and trigger boxes.
        """
        # Get the current location of the vehicle
        vehicle_location = carla_interface_process.agent_objects['My Vehicle_1'].shared_variables.transform.location

        # Check if the vehicle has reached a waypoint and update the control accordingly
        self.steer_to_waypoint(carla_interface_process, vehicle_location)

        # Check if the vehicle is inside any trigger box and handle the behavior
        boxtrigg = self.adjust_speed(carla_interface_process, vehicle_location)
        if boxtrigg == "final":
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})

        ####DEFINE THE TRAJECTORY OF THE CAR BASED ON THIS WAY POINTS

    def define_manual_waypoints(self, trajectory_path):
        """
        Manually define waypoints for the circuit.
        Each waypoint is a carla.Transform(location, rotation).
        """
        waypoints = []
        try:

            # Load the CSV file
            df = pd.read_csv(trajectory_path, header=None)
            # Convert each row into a CARLA waypoint
            for _, row in df.iterrows():
                transform = carla.Transform(
                    carla.Location(x=row[1], y=row[2], z=row[3]),
                    carla.Rotation(yaw=row[4])  # Assuming 'heading' represents yaw
                )
                waypoints.append(transform)

            print(f"Loaded {len(waypoints)} waypoints from file.")
        except Exception as e:
            print(f"Error loading waypoints: {e}")
        return waypoints

    def load_trigger_boxes(self):
        """
        Load trigger boxes for Trial 1.
        """
        return [
            {'location': carla.Location(x=14.18303711, y=-206.75150391, z=1.05), 'behavior': 'stop'},
            {'location': carla.Location(x=313.97119141, y=-113.04113281, z=1.05), 'behavior': 'continue'},
            {'location': carla.Location(x=346.77320312, y=-121.63306641, z=1.05), 'behavior': 'stop'},
            {'location': carla.Location(x=352.06660156, y=-156.83760742, z=1.05), 'behavior': 'continue'},
            {'location': carla.Location(x=331.06691406, y=-249.96021484, z=1.05), 'behavior': 'stop'},
            {'location': carla.Location(x=291.45935547, y=-249.73994141, z=1.05), 'behavior': 'continue'},
            {'location': carla.Location(x=290.91568359, y=-232.86884766, z=1.05), 'behavior': 'final'},
            # Slight slowdown
            # {'location': carla.Location(x=350, y=250, z=0), 'behavior': 'slowdown', 'target_speed': 20},  # Slowdown box
        ]

    def steer_to_waypoint(self, carla_interface_process, vehicle_location):
        """
        Calls the vehicle's method to steer to the next waypoint.
        """
        my_vehicle = carla_interface_process.agent_objects['My Vehicle_1']  # Access vehicle object
        my_vehicle.steer_to_waypoint()  # Delegate the steering logic to the vehicle class

    def adjust_speed(self, carla_interface_process, vehicle_location):
        """
        Calls the vehicle's method to adjust speed based on trigger box behavior.
        """
        my_vehicle = carla_interface_process.agent_objects['My Vehicle_1']  # Access vehicle object
        boxtrigg = my_vehicle.adjust_speed(vehicle_location,
                                           self.trigger_boxes)  # Delegate the speed adjustment to the vehicle class
        return boxtrigg
