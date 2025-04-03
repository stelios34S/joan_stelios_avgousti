import random, os, math
import numpy as np
import threading
from tools.carlaimporter import carla
import pandas as pd
from PyQt5 import uic, QtWidgets
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from modules.joanmodules import JOANModules
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox


##TODO: WE NEED TO CUSTOM MAKE THIS TO BE OUR OWN VEHICLE
class MyVehicleSettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings, module_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.module_manager = module_manager
        self.carla_interface_overall_settings = self.module_manager.module_settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), "ui/my_vehicle_settings_ui.ui"), self)
        self.msg_box = QMessageBox()
        self.msg_box.setTextFormat(QtCore.Qt.RichText)

        self.button_box_egovehicle_settings.button(self.button_box_egovehicle_settings.RestoreDefaults).clicked.connect(
            self._set_default_values)
        self.btn_apply_parameters.clicked.connect(self.update_parameters)
        self.btn_update.clicked.connect(lambda: self.update_settings(self.settings))
        self.display_values()

        self.update_settings(self.settings)

    def show(self):
        self.update_settings(self.settings)
        super().show()

    def update_parameters(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_haptic_controllers.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
        for settings in self.carla_interface_overall_settings.agents.values():
            if settings.identifier != self.settings.identifier:  # exlude own settings
                if settings.selected_spawnpoint == self.combo_spawnpoints.currentText() and settings.selected_spawnpoint != 'None':
                    self.msg_box.setText('This spawnpoint was already chosen for another agent \n'
                                         'resetting spawnpoint to None')
                    self.msg_box.exec()
                    self.settings.selected_spawnpoint = 'None'
                    break
                else:
                    self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()

        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        self.display_values()

    def accept(self):
        self.settings.velocity = self.spin_velocity.value()
        self.settings.selected_input = self.combo_input.currentText()
        self.settings.selected_controller = self.combo_haptic_controllers.currentText()
        self.settings.selected_car = self.combo_car_type.currentText()
        self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
        for settings in self.carla_interface_overall_settings.agents.values():
            if settings.identifier != self.settings.identifier:  # exlude own settings
                if settings.selected_spawnpoint == self.combo_spawnpoints.currentText() and settings.selected_spawnpoint != 'None':
                    self.msg_box.setText('This spawnpoint was already chosen for another agent \n'
                                         'resetting spawnpoint to None')
                    self.msg_box.exec()
                    self.settings.selected_spawnpoint = 'None'
                    break
            else:
                self.settings.selected_spawnpoint = self.combo_spawnpoints.currentText()
        self.settings.set_velocity = self.check_box_set_vel.isChecked()
        super().accept()

    def display_values(self, settings_to_display=None):
        if not settings_to_display:
            settings_to_display = self.settings

        idx_controller = self.combo_haptic_controllers.findText(settings_to_display.selected_controller)
        self.combo_haptic_controllers.setCurrentIndex(idx_controller)

        idx_input = self.combo_input.findText(settings_to_display.selected_input)
        self.combo_input.setCurrentIndex(idx_input)

        idx_car = self.combo_car_type.findText(settings_to_display.selected_car)
        self.combo_car_type.setCurrentIndex(idx_car)

        self.combo_spawnpoints.setCurrentText(settings_to_display.selected_spawnpoint)

        self.spin_velocity.setValue(settings_to_display.velocity)
        self.check_box_set_vel.setChecked(settings_to_display.set_velocity)

    def _set_default_values(self):
        self.display_values(AgentTypes.MY_VEHICLE.settings())

    def update_settings(self, settings):
        try:
            # Update hardware inputs according to current settings:
            self.combo_input.clear()
            self.combo_input.addItem('None')
            HardwareManagerSettings = self.module_manager.central_settings.get_settings(JOANModules.HARDWARE_MANAGER)
            for inputs in HardwareManagerSettings.inputs.values():
                self.combo_input.addItem(str(inputs))
            idx = self.combo_input.findText(
                settings.selected_input)
            if idx != -1:
                self.combo_input.setCurrentIndex(idx)

            # update available vehicles
            self.combo_car_type.clear()
            self.combo_car_type.addItem('None')
            self.combo_car_type.addItems(self.module_manager.vehicle_tags)
            idx = self.combo_car_type.findText(settings.selected_car)
            if idx != -1:
                self.combo_car_type.setCurrentIndex(idx)

            # update available spawn_points:
            self.combo_spawnpoints.clear()
            self.combo_spawnpoints.addItem('None')
            self.combo_spawnpoints.addItems(self.module_manager.spawn_points)
            idx = self.combo_spawnpoints.findText(
                settings.selected_spawnpoint)
            if idx != -1:
                self.combo_spawnpoints.setCurrentIndex(idx)

            # update available controllers according to current settings:
            self.combo_haptic_controllers.clear()
            self.combo_haptic_controllers.addItem('None')
            HapticControllerManagerSettings = self.module_manager.central_settings.get_settings(
                JOANModules.HAPTIC_CONTROLLER_MANAGER)
            for haptic_controller in HapticControllerManagerSettings.haptic_controllers.values():
                self.combo_haptic_controllers.addItem(str(haptic_controller))
            idx = self.combo_haptic_controllers.findText(
                settings.selected_controller)
            if idx != -1:
                self.combo_haptic_controllers.setCurrentIndex(idx)
        except AttributeError:
            # Catching attribute error when using default car settings
            pass


class MyVehicleProcess:
    def __init__(self, carla_mp, settings, shared_variables):
        self.settings = settings
        self.shared_variables = shared_variables
        self.carlainterface_mp = carla_mp

        self._control = carla.VehicleControl()
        if self.settings.selected_car != 'None':
            self._BP = random.choice(
                self.carlainterface_mp.vehicle_blueprint_library.filter("vehicle." + self.settings.selected_car))
        self.world_map = self.carlainterface_mp.world.get_map()
        self.trajectory_file_path = "modules/carlainterface/carlainterface_agentclasses/trajectories/trajectory1.csv"

        ####DEFINE TRIGGER BOXES TO STOP OR SLO DOWN
        # Define speed adjustment trigger boxes
        self.trigger_boxes = [

        ]
        # Define waypoints the car will follow
        #self.waypoints = self.define_manual_waypoints(self.trajectory_file_path)
        self.current_waypoint_index = 0
        self.waypoints = []
        self.is_in_override_mode = False
        self.flag = False
        ## Holds the current trigger which is active (continue/stop)
        self.trigger_active = None
        ## Here to allow us to mess wit hthe speed while in cruise control
        self.user_override_speed = self.settings.velocity
        self.reset_speed = 0
        ###Resets the speed to cruise control after trigger box
        self.recovery_timer = None  # Store a reference to the timer

        torque_curve = []
        gears = []

        torque_curve.append(carla.Vector2D(x=0, y=600))
        torque_curve.append(carla.Vector2D(x=14000, y=600))
        gears.append(carla.GearPhysicsControl(ratio=7.73, down_ratio=0.5, up_ratio=1))
        gears.append(carla.GearPhysicsControl(ratio=7.73, down_ratio=0.5, up_ratio=1))

        if self.settings.selected_spawnpoint != 'None':
            if self.settings.selected_car != 'None':
                self.spawned_vehicle = self.carlainterface_mp.world.spawn_actor(self._BP,
                                                                                self.carlainterface_mp.spawn_point_objects[
                                                                                    self.carlainterface_mp.spawn_points.index(
                                                                                        self.settings.selected_spawnpoint)])
                physics = self.spawned_vehicle.get_physics_control()
                physics.torque_curve = torque_curve
                physics.max_rpm = 14000
                physics.moi = 1.5
                physics.final_ratio = 1
                physics.clutch_strength = 1000  # very big no clutch
                physics.final_ratio = 1  # ratio from transmission to wheels
                physics.forward_gears = gears
                physics.mass = 2316
                physics.drag_coefficient = 0.24
                physics.gear_switch_time = 0
                self.spawned_vehicle.apply_physics_control(physics)
    ###RESPONSIBLE TOWARDS STEERING FOR THE WAYPOINTS
    def steer_to_waypoint(self):
        """
        Adjusts the vehicle's steering angle to follow the waypoints.
        """

        next_wp = self.get_next_waypoint(self.waypoints)
        if next_wp:
            vehicle_transform = self.spawned_vehicle.get_transform()
            vehicle_location = vehicle_transform.location
            vehicle_rotation = vehicle_transform.rotation.yaw  # Vehicle heading

            target_location = next_wp['transform'].location
            target_vector = np.array([target_location.x - vehicle_location.x, target_location.y - vehicle_location.y])
            vehicle_vector = np.array(
                [math.cos(math.radians(vehicle_rotation)), math.sin(math.radians(vehicle_rotation))])

            # Compute the steering angle error
            angle_diff = np.arctan2(np.cross(vehicle_vector, target_vector), np.dot(vehicle_vector, target_vector))
            controller = PIDController(kp=0.2,ki=0.05,kd=0.8)
            steering_correction = controller.compute(angle_diff)
            # Apply a scaling factor to avoid over-steering
            if abs(steering_correction) < 0.09:
                steering_correction = 0
            self._control.steer = (0.9 * self._control.steer) + (0.1 * steering_correction)

            # If close enough, move to next waypoint
            if vehicle_location.distance(target_location) < 5:  # Adjust distance threshold if needed

                self.current_waypoint_index += 1
                #print(f"Moving to waypoint {self.current_waypoint_index}")

    def load_scenario_data(self,scenario_identifier,trajectory_path):
            if scenario_identifier == "trial_1":
                self.waypoints = self.define_manual_waypoints(trajectory_path)
                self.trigger_boxes = self.load_trigger_boxes(scenario_identifier)
                self.flag = True

    ####GET THE NEXT WAYPOINT IN THE LIST
    def get_next_waypoint(self,waypoints):
        """
        Gets the next waypoint in the list.
        """
        if self.current_waypoint_index >= len(waypoints):
            print("✅ Circuit Completed!")

            return None  # No more waypoints, the circuit is finished
        return waypoints[self.current_waypoint_index]
    def load_trigger_boxes(self,scenario_identifier):
        if scenario_identifier == "trial_1":
            triggerlist =[
            {'location': carla.Location(x=13.54254761, y=-219.77351562, z=1.05), 'behavior': 'continue'},
            {'location': carla.Location(x=352.75347656, y=-192.88890625, z=1.05), 'behavior': 'continue'},
            {'location': carla.Location(x=341.73339844, y=-118.74054688, z=1.05), 'behavior': 'stop'},
            {'location': carla.Location(x=297.74673828, y=-223.13464844, z=1.05), 'behavior': 'final'}]
            return triggerlist
        if scenario_identifier == "trial_2":
            return []
        if scenario_identifier== "trial_3":
            return []
        # Slight slowdown
        # {'location': carla.Location(x=350, y=250, z=0), 'behavior': 'slowdown', 'target_speed': 20},  # Slowdown box

    ####DEFINE THE TRAJECTORY OF THE CAR BASED ON THIS WAY POINTS
    def define_manual_waypoints(self,trajectory_path):
        """
        Manually define waypoints for the circuit.
        Each waypoint is a carla.Transform(location, rotation).
        """
        waypoints = []
        try:

            # Load the CSV file
            df = pd.read_csv(trajectory_path,header=None)
            # Convert each row into a CARLA waypoint
            for _, row in df.iterrows():
                transform = carla.Transform(
                    carla.Location(x=row[1], y=row[2], z=row[3]),
                    carla.Rotation(yaw=row[4])  # Assuming 'heading' represents yaw
                )
                speed = row[7]  # Speed is stored in column 8 (index 7)
                waypoints.append({'transform':transform, 'speed':speed})

            print(f"✅ Loaded {len(waypoints)} waypoints from file.")
        except Exception as e:
            print(f"❌ Error loading waypoints: {e}")
        return waypoints

    def get_current_speed(self):
        """
        Calculates the current speed of the vehicle in km/h.
        """
        if not hasattr(self, 'spawned_vehicle') or self.spawned_vehicle is None:
            return 0  # Avoid errors if the vehicle doesn't exist

        velocity = self.spawned_vehicle.get_velocity()
        current_speed = math.sqrt(
            velocity.x ** 2 +
            velocity.y ** 2 +
            velocity.z ** 2
        ) * 3.6  # Convert to km/h

        return current_speed

    def do(self):
        if self.settings.selected_input != 'None' and hasattr(self, 'spawned_vehicle'):

            ###STEERING FUNCTION now invoked from scenario
            self.steer_to_waypoint()
            ###STEERING FUNCTION


            # self._control.steer = self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].steering_angle / math.radians(450)

            self._control.reverse = self.carlainterface_mp.shared_variables_hardware.inputs[
                self.settings.selected_input].reverse
            self._control.hand_brake = self.carlainterface_mp.shared_variables_hardware.inputs[
                self.settings.selected_input].handbrake
            self._control.brake = self.carlainterface_mp.shared_variables_hardware.inputs[
                self.settings.selected_input].brake

            if self.settings.set_velocity:
                if self.flag and self.trigger_active != "final":
                    current_waypoint = self.waypoints[self.current_waypoint_index]
                    if not self.is_in_override_mode:
                        self.user_override_speed = current_waypoint['speed']  # Target speed from waypoint
                        vel_error = self.user_override_speed*3.6 - self.get_current_speed()
                    else:
                        vel_error = self.user_override_speed  - self.get_current_speed()
                    self.reset_speed = current_waypoint['speed']*3.6
                    vel_error_rate = (math.sqrt(
                        self.spawned_vehicle.get_acceleration().x ** 2 +
                        self.spawned_vehicle.get_acceleration().y ** 2 +
                        self.spawned_vehicle.get_acceleration().z ** 2) * 3.6)
                    error_velocity = [vel_error, vel_error_rate]

                    pd_vel_output = self.velocity_PD_controller(error_velocity)
                    if pd_vel_output < 0:
                        self._control.brake = -pd_vel_output
                        self._control.throttle = 0
                        if pd_vel_output < -1:
                            self._control.brake = 1
                    elif pd_vel_output > 0:
                        if self._control.brake == 0:
                            self._control.throttle = pd_vel_output
                        else:
                            self._control.throttle = 0
            else:
                self._control.throttle = self.carlainterface_mp.shared_variables_hardware.inputs[
                    self.settings.selected_input].throttle

            ##################ADJUST SPEED ON LOCATION################################
            vehicle_location = self.spawned_vehicle.get_transform().location
            trigger_behaviour = self.adjust_speed_trigger(vehicle_location=vehicle_location)
            # if self.flag:
            #     current_waypoint = self.waypoints[self.current_waypoint_index]
            #     if current_waypoint:
            #         target_speed = current_waypoint['speed']  # Get the target speed from the waypoint data
            #         self.adjust_speed(target_speed)  # Adjust speed to match trajectory

            ##################### INFORM BUTTON (I key)(TAP) ############################
            if self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].inform:
                #print("KATI KATI")
                self.is_in_override_mode = True
                if self.trigger_active == "stop":  # If the box wants a stop, brake harder
                    self._control.brake = 1.0  # Max braking force
                    self._control.throttle = 0
                    self.user_override_speed = 0
                elif self.trigger_active == "continue":
                    self.user_override_speed = max(15, self.reset_speed - 10)  # Temporary slowdown
                else:
                    self.user_override_speed = max(25, self.reset_speed - 15)
                self.start_recovery_timer(7)


            ##################### INTERVENE BUTTON (J key) ############################
            if self.carlainterface_mp.shared_variables_hardware.inputs[self.settings.selected_input].intervene:

                self.is_in_override_mode = True
                if self.trigger_active == "stop":
                    #TODO: ONLY FLIMSY PART######
                    # Car originally planned to stop -> Override and keep moving
                    self.user_override_speed = max(15, self.reset_speed)
                elif self.trigger_active == "continue":
                    # Reduce speed to zero, then recover after 5 seconds
                    self.user_override_speed = 0
                    self._control.brake = 1
                else:
                    self.user_override_speed = 0
                    self._control.brake = 1
                # Set recovery timer (after 5 sec, return to normal speed)
                self.start_recovery_timer(7)



            self.spawned_vehicle.apply_control(self._control)
            try:
                self.calculate_plotter_road_arrays()
            except IndexError:
                pass

        self.set_shared_variables()


    def start_recovery_timer(self, time):
        """Starts a timer to restore speed after a delay."""
        if self.recovery_timer and self.recovery_timer.is_alive():
            self.recovery_timer.cancel()  # Cancel any existing timer before starting a new one

        self.recovery_timer = threading.Timer(time, self.reset_to_standard_speed)  # 5-second delay
        self.recovery_timer.start()

    def reset_to_standard_speed(self):
        """Gradually restores the car to its normal speed after interventions."""
        self.user_override_speed = self.reset_speed  # Restore standard velocity
        self.is_in_override_mode = False


    def adjust_speed_trigger(self, vehicle_location):
        """
        Adjusts vehicle speed based on predefined trigger boxes.
        """
        new_trigger = None  # Default to None

        for box in self.trigger_boxes:
            if vehicle_location.distance(box['location']) < 4:  # Inside trigger box
                new_trigger = box['behavior']
                if new_trigger == "final":
                    self.carlainterface_mp.pipe_comm.send({"stop_all_modules": True})
                break  # Exit loop once a trigger is found
        # if box['behavior'] == "stop":
        #     self._control.brake = 0.5  # medium braking force
        #     self._control.throttle = 0
        #     self.user_override_speed = 0
        #     self.start_recovery_timer(7)
        #
        # if box['behavior'] == "continue":
        #     self.user_override_speed = max(10,
        #                                    self.user_override_speed - 20)  # Prevent zero speed in movement areas
        #     self.start_recovery_timer(5)
        # if box['behavior'] == "final":
        #     self.user_override_speed = 0

        # Only reset trigger if the vehicle left the last trigger box
        if self.trigger_active and new_trigger is None:
            self.trigger_active = None
            #self.display_hud_message("Exited Trigger Box")
        self.trigger_active = new_trigger  # Store active trigger behavior
        return new_trigger


    def display_hud_message(self, message, duration=2):
        if hasattr(self, 'spawned_vehicle'):
            vehicle_transform = self.spawned_vehicle.get_transform()
            hud_location = vehicle_transform.location  # Adjust as needed
            carlaLoc = carla.Location(x=-0.45, y=0, z=0.7)
            newloc = hud_location + carlaLoc
            self.carlainterface_mp.world.debug.draw_string(
                newloc,
                message,
                draw_shadow=True,
                color=carla.Color(r=0, g=0, b=0),
                life_time=duration
            )

    def destroy(self):
        if hasattr(self, 'spawned_vehicle') and self.spawned_vehicle is not None:
            self.spawned_vehicle.destroy()
            self.spawned_vehicle = None  # Mark the vehicle as destroyed

    def velocity_PD_controller(self, vel_error):
        _kp_vel = 50
        _kd_vel = 1
        temp = _kp_vel * vel_error[0] + _kd_vel * vel_error[1]

        if temp > 100:
            temp = 100

        output = temp / 100

        return output

    def calculate_plotter_road_arrays(self):
        # If the vehicle is destroyed, skip calculating the road arrays.
        if not hasattr(self, 'spawned_vehicle') or self.spawned_vehicle is None:
            return
        data_road_x = []
        data_road_x_inner = []
        data_road_x_outer = []
        data_road_y = []
        data_road_y_inner = []
        data_road_y_outer = []
        data_road_psi = []
        data_road_lanewidth = []

        if self.spawned_vehicle is not None:
            vehicle_location = self.spawned_vehicle.get_location()
            closest_waypoint = self.world_map.get_waypoint(vehicle_location, project_to_road=True)

            # previous points
            previous_waypoints = []
            for a in reversed(range(1, 26)):
                previous_waypoints.append(closest_waypoint.previous(a))

            # next
            next_waypoints = []
            for a in range(1, 26):
                next_waypoints.append(closest_waypoint.next(a))

            for waypoints in previous_waypoints:
                data_road_x.append(waypoints[0].transform.location.x)
                data_road_y.append(waypoints[0].transform.location.y)
                data_road_lanewidth.append(waypoints[0].lane_width)

            for waypoints in next_waypoints:
                data_road_x.append(waypoints[0].transform.location.x)
                data_road_y.append(waypoints[0].transform.location.y)
                data_road_lanewidth.append(waypoints[0].lane_width)

            pos_array = np.array([[data_road_x], [data_road_y]])
            diff = np.transpose(np.diff(pos_array))

            x_unit_vector = np.array([[1], [0]])
            for row in diff:
                data_road_psi.append(self.compute_angle(row.ravel(), x_unit_vector.ravel()))

            data_road_psi.append(0)

            iter_x = 0
            for roadpoint_x in data_road_x:
                data_road_x_outer.append(
                    roadpoint_x - math.sin(data_road_psi[iter_x]) * data_road_lanewidth[iter_x] / 2)
                data_road_x_inner.append(
                    roadpoint_x + math.sin(data_road_psi[iter_x]) * data_road_lanewidth[iter_x] / 2)
                iter_x = iter_x + 1

            iter_y = 0
            for roadpoint_y in data_road_y:
                data_road_y_outer.append(
                    roadpoint_y - math.cos(data_road_psi[iter_y]) * data_road_lanewidth[iter_y] / 2)
                data_road_y_inner.append(
                    roadpoint_y + math.cos(data_road_psi[iter_y]) * data_road_lanewidth[iter_y] / 2)
                iter_y = iter_y + 1

            # set shared road variables:
            self.shared_variables.data_road_x = data_road_x
            self.shared_variables.data_road_x_inner = data_road_x_inner
            self.shared_variables.data_road_x_outer = data_road_x_outer
            self.shared_variables.data_road_y = data_road_y
            self.shared_variables.data_road_y_inner = data_road_y_inner
            self.shared_variables.data_road_y_outer = data_road_y_outer
            self.shared_variables.data_road_psi = data_road_psi
            self.shared_variables.data_road_lanewidth = data_road_lanewidth

    def compute_angle(self, v1, v2):
        arg1 = np.cross(v1, v2)
        arg2 = np.dot(v1, v2)
        angle = np.arctan2(arg1, arg2)
        return angle

    def set_shared_variables(self):
        if hasattr(self, 'spawned_vehicle'):
            rotation = self.spawned_vehicle.get_transform().rotation
            self.shared_variables.transform = [self.spawned_vehicle.get_transform().location.x,
                                               self.spawned_vehicle.get_transform().location.y,
                                               self.spawned_vehicle.get_transform().location.z,
                                               rotation.yaw,
                                               rotation.pitch,
                                               rotation.roll]
            linear_velocity = self.spawned_vehicle.get_velocity()
            self.shared_variables.velocities_in_world_frame = [linear_velocity.x,
                                                               linear_velocity.y,
                                                               linear_velocity.z,
                                                               self.spawned_vehicle.get_angular_velocity().x,
                                                               self.spawned_vehicle.get_angular_velocity().y,
                                                               self.spawned_vehicle.get_angular_velocity().z]

            rotation_matrix = self.get_rotation_matrix_from_carla(rotation.roll, rotation.pitch, rotation.yaw)
            velocities_in_vehicle_frame = np.linalg.inv(rotation_matrix) @ np.array(
                [linear_velocity.x, linear_velocity.y, linear_velocity.z])
            self.shared_variables.velocities_in_vehicle_frame = velocities_in_vehicle_frame

            self.shared_variables.accelerations = [self.spawned_vehicle.get_acceleration().x,
                                                   self.spawned_vehicle.get_acceleration().y,
                                                   self.spawned_vehicle.get_acceleration().z]
            latest_applied_control = self.spawned_vehicle.get_control()
            self.shared_variables.applied_input = [float(latest_applied_control.steer),
                                                   float(latest_applied_control.reverse),
                                                   float(latest_applied_control.hand_brake),
                                                   float(latest_applied_control.brake),
                                                   float(latest_applied_control.throttle)]

    @staticmethod
    def get_rotation_matrix_from_carla(roll, pitch, yaw, degrees=True):
        """ calculation based on this github issue: https://github.com/carla-simulator/carla/issues/58 because carla uses some rather unconventional conventions."""
        if degrees:
            roll, pitch, yaw = np.radians([roll, pitch, yaw])

        yaw_matrix = np.array([
            [math.cos(yaw), -math.sin(yaw), 0],
            [math.sin(yaw), math.cos(yaw), 0],
            [0, 0, 1]
        ])

        pitch_matrix = np.array([
            [math.cos(pitch), 0, -math.sin(pitch)],
            [0, 1, 0],
            [math.sin(pitch), 0, math.cos(pitch)]
        ])

        roll_matrix = np.array([
            [1, 0, 0],
            [0, math.cos(roll), math.sin(roll)],
            [0, -math.sin(roll), math.cos(roll)]
        ])

        rotation_matrix = yaw_matrix @ pitch_matrix @ roll_matrix
        return rotation_matrix


class PIDController:
    """Basic PID controller for smoother steering adjustments."""

    def __init__(self, kp=1.0, ki=0.0, kd=0.1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error):
        """Calculate the PID output based on error (steering correction)."""
        self.integral += error
        derivative = error - self.prev_error
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return max(-1.0, min(1.0, output))  # Clamp output to valid steering range (-1 to 1)


class MyVehicleSettings:
    """
    Class containing the default settings for an egovehicle
    """

    def __init__(self, identifier='My'):
        """
        Initializes the class with default variables
        """
        self.selected_input = 'None'
        self.selected_controller = 'None'
        self.selected_spawnpoint = 'Spawnpoint 0'
        self.selected_car = 'hapticslab.audi'
        self.velocity = 80
        self.set_velocity = False
        self.identifier = identifier

        self.agent_type = AgentTypes.MY_VEHICLE.value

    def as_dict(self):
        return self.__dict__

    def set_from_loaded_dict(self, loaded_dict):
        for key, value in loaded_dict.items():
            self.__setattr__(key, value)

    def __str__(self):
        return self.identifier
