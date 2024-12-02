import numpy as np
import time
import json
import redis
import math
from enum import Enum, auto
from dataclasses import dataclass
from scipy.spatial.transform import Rotation as R
import ipdb

DEG_TO_RAD = math.pi / 180.0

class State(Enum):
    INIT = auto()
    PICK = auto()
    GOING_TO_CONTACT = auto()
    SURFACE_ALIGNMENT = auto()
    FINISH = auto()

@dataclass
class RedisKeys:
    panda_goal_position: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::goal_position"
    panda_goal_orientation: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::goal_orientation"
    panda_current_position: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::current_position"
    panda_current_orientation: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::current_orientation"
    allegro_fingers_goal_position: str = "opensai::controllers::panda_with_allegro::cartesian_controller::gripper_fingers::goal_position"
    sensed_force: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::sensed_force"
    force_space_dimension: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::force_space_dimension"
    force_space_axis: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::force_space_axis"
    closed_loop_force_control: str = "opensai::controllers::panda_with_allegro::cartesian_controller::cartesian_task::closed_loop_force_control"
    object_current_position: str = "opensai::sensors::Cylinder::object_pose"
    table_goal_angles: str = "opensai::controllers::Table::tilt_controller::tilt_task::goal_position"

redis_keys = RedisKeys()

# Redis client
redis_client = redis.Redis()

# Configurations
object_initial_position = np.array([0.5, -0.1, 0.15])  # Initial object position
contact_goal_position = np.array([0.6, 0.0, 0.175])    # Goal position for contact
pre_pick_offset = np.array([0.0, 0.0, 0.1])            # Offset for pre-pick
fingers_open_position = [0.05] * 16
fingers_closed_position = [0.01] * 16
contact_force_threshold = -15.0

# Allegro hand specific positions (4 fingers with 4 joints each)
fingers_open_position = [0.05] * 16
fingers_closed_position = [0.01] * 16

table_position = np.array([0.6, 0.3, 0.2])  # Position of the table
table_goal_angles = np.array([0.0, 0.0])

state = State.INIT
picked = False

# Timing for loop
loop_time = 0.0
dt = 0.01
loop_step = 0

try:
    init_time = time.perf_counter_ns() * 1e-9  # Initialize timer

    while True:
        # Time control
        loop_time += dt
        time.sleep(
            max(0, loop_time - (time.perf_counter_ns() * 1e-9 - init_time))
        )

        # Table tilt control
        if (loop_step % 1000) == 0:
            table_goal_angles[0] = 12.0 * DEG_TO_RAD
        if (loop_step % 1000) == 500:
            table_goal_angles[0] = -12.0 * DEG_TO_RAD
        if (loop_step % 1500) == 0:
            table_goal_angles[1] = 18.0 * DEG_TO_RAD
        if (loop_step % 1500) == 750:
            table_goal_angles[1] = -18.0 * DEG_TO_RAD

        redis_client.set(redis_keys.table_goal_angles, json.dumps(table_goal_angles.tolist()))

        # Add debug prints to track Redis key retrieval and transformations
        current_position_raw = redis_client.get(redis_keys.panda_current_position)
        print(f"Debug: Raw Redis value for {redis_keys.panda_current_position}: {current_position_raw}")

        if current_position_raw is None:
            print(f"Error: Key '{redis_keys.panda_current_position}' is missing or not set.")
            current_position = np.zeros(3)  # Default value for safety
        else:
            try:
                current_position = np.array(json.loads(current_position_raw))
                print(f"Debug: Parsed current_position: {current_position}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for key '{redis_keys.panda_current_position}': {e}")
                current_position = np.zeros(3)  # Default value for safety

        current_orientation_raw = redis_client.get(redis_keys.panda_current_orientation)
        print(f"Debug: Raw Redis value for {redis_keys.panda_current_orientation}: {current_orientation_raw}")

        if current_orientation_raw is None:
            print(f"Error: Key '{redis_keys.panda_current_orientation}' is missing or not set.")
            current_orientation = np.zeros(3)  # Default value for safety
        else:
            try:
                current_orientation = np.array(json.loads(current_orientation_raw))
                print(f"Debug: Parsed current_orientation: {current_orientation}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for key '{redis_keys.panda_current_orientation}': {e}")
                current_orientation = np.zeros(3)  # Default value for safety

        # State machine logic
        pre_pick_position = object_initial_position + pre_pick_offset

        # State machine logic
        # State machine logic
        if state == State.INIT:
            print("State: INIT")
            redis_client.set(redis_keys.panda_goal_position, json.dumps(pre_pick_position.tolist()))
            redis_client.set(redis_keys.panda_goal_orientation, json.dumps(
                R.from_euler('xyz', [180 * DEG_TO_RAD, 0, 90 * DEG_TO_RAD]).as_matrix().tolist()
            ))
            print(f"Setting goal position to pre-pick: {pre_pick_position}")
            state = State.PICK

        elif state == State.PICK:
            # ipdb.set_trace()
            print("State: PICK")
            print(f"Current Position: {current_position}")
            print(f"Pre-pick Position: {pre_pick_position}")
            print("State: PICK")
            if np.linalg.norm(current_position - pre_pick_position) > 0.05 and not picked:
                print("Moving to Pick Position")
                redis_client.set(redis_keys.panda_goal_position, json.dumps(object_initial_position.tolist()))
            elif np.linalg.norm(current_position - object_initial_position) < 0.05 and not picked:
                print("Closing Fingers")
                redis_client.set(redis_keys.allegro_fingers_goal_position, json.dumps(fingers_closed_position))
                time.sleep(0.5)
                picked = True
                print("Object Picked")
                redis_client.set(redis_keys.panda_goal_position, json.dumps(pre_pick_position.tolist()))
            elif picked:
                print("Moving to Pre-Contact Position")
                redis_client.set(redis_keys.panda_goal_position, json.dumps(table_position.tolist()))
                state = State.GOING_TO_CONTACT

        elif state == State.GOING_TO_CONTACT:
            print("State: GOING_TO_CONTACT")
            redis_client.set(redis_keys.panda_goal_position, json.dumps(contact_goal_position.tolist()))
            sensed_force_raw = redis_client.get(redis_keys.sensed_force)
            if sensed_force_raw is None:
                print(f"Error: {redis_keys.sensed_force} is missing.")
                break
            sensed_force = np.array(json.loads(sensed_force_raw))
            print(f"Sensed Force: {sensed_force}")

            if sensed_force[2] < contact_force_threshold:
                print("Contact established. Switching to SURFACE_ALIGNMENT.")
                redis_client.set(redis_keys.force_space_dimension, "1")
                redis_client.set(redis_keys.force_space_axis, json.dumps([0, 0, 1]))
                redis_client.set(redis_keys.closed_loop_force_control, "1")
                state = State.SURFACE_ALIGNMENT

        elif state == State.SURFACE_ALIGNMENT:
            print("State: SURFACE_ALIGNMENT")
            redis_client.set(redis_keys.force_space_axis, json.dumps([0, 0, 1]))
            redis_client.set(redis_keys.closed_loop_force_control, "1")
            time.sleep(1.0)  # Simulate alignment
            print("Surface alignment completed.")
            state = State.FINISH

        elif state == State.FINISH:
            print("State: FINISH")
            print("Task completed successfully.")
            break
        loop_step+=1

except KeyboardInterrupt:
    print("Program interrupted.")