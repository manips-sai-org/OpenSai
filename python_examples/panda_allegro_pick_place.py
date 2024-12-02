import numpy as np
import time
import json
import redis
from enum import Enum, auto
from dataclasses import dataclass
from scipy.spatial.transform import Rotation as R

DEG_TO_RAD = np.pi / 180.0

class State(Enum):
    INIT = auto()
    PICK = auto()
    PLACE = auto()
    FINISH = auto()

@dataclass
class RedisKeys:
    cartesian_task_goal_position: str = "opensai::controllers::Panda::cartesian_controller::cartesian_task::goal_position"
    cartesian_task_goal_orientation: str = "opensai::controllers::Panda::cartesian_controller::cartesian_task::goal_orientation"
    cartesian_task_current_position: str = "opensai::controllers::Panda::cartesian_controller::cartesian_task::current_position"
    cartesian_task_current_orientation: str = "opensai::controllers::Panda::cartesian_controller::cartesian_task::current_orientation"
    allegro_fingers_goal_position: str = "opensai::controllers::AllegroHand::finger_controller::goal_position"
    object_current_position: str = "opensai::sensors::Cylinder::object_pose"
    active_controller: str = "opensai::controllers::Panda::active_controller_name"
    config_file_name: str = "::sai2-interfaces-webui::config_file_name"

redis_keys = RedisKeys()

config_file_for_this_example = "allegro_hand_world.urdf"
controller_to_use = "cartesian_controller"

place_goal_position = np.array([0.4, -0.3, 0.2])  # Target position for placing the cylinder

redis_client = redis.Redis()

# Initialization
object_position = np.array(json.loads(redis_client.get(redis_keys.object_current_position)))[0:3, 3]
pre_pick_position = object_position + np.array([0.0, 0.0, 0.1])
pick_position = object_position
pre_place_position = place_goal_position + np.array([0.0, 0.0, 0.1])
place_position = place_goal_position

# Allegro hand specific positions (4 fingers with 4 joints each)
fingers_open_position = [0.05] * 16  # Open all joints
fingers_closed_position = [0.01] * 16  # Close all joints

picked = False
placed = False

# State machine
state = State.INIT

try:
    while True:
        # Get current positions
        current_position = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_current_position)))
        current_orientation = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_current_orientation)))

        if state == State.INIT:
            print("INIT")
            redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pre_pick_position.tolist()))
            redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(R.from_euler('xyz', [180 * DEG_TO_RAD, 0, 90 * DEG_TO_RAD]).as_matrix().tolist()))
            redis_client.set(redis_keys.allegro_fingers_goal_position, json.dumps(fingers_open_position))
            state = State.PICK

        elif state == State.PICK:
            print("PICK")
            print("Current Position:", current_position)
            print("Pick Position:", pick_position)
            print("Distance to Pick Position:", np.linalg.norm(current_position - pick_position))
    
            if np.linalg.norm(current_position - pre_pick_position) < 0.05 and not picked:
                print("Moving to Pick Position")
                redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pick_position.tolist()))
            if np.linalg.norm(current_position - pick_position) < 0.05 and not picked:
                print("Closing Fingers")
                redis_client.set(redis_keys.allegro_fingers_goal_position, json.dumps(fingers_closed_position))
                time.sleep(0.5)
                picked = True
                print("Object Picked")
                redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pre_pick_position.tolist()))
            if np.linalg.norm(current_position - pre_pick_position) < 0.05 and picked:
                print("Moving to Pre-Place Position")
                redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pre_place_position.tolist()))
                state = State.PLACE

        elif state == State.PLACE:
            print("PLACE")
            if np.linalg.norm(current_position - pre_place_position) < 0.01 and not placed:
                redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(place_position.tolist()))
            elif np.linalg.norm(current_position - place_position) < 0.01 and not placed:
                print("Opening Fingers")
                redis_client.set(redis_keys.allegro_fingers_goal_position, json.dumps(fingers_open_position))
                time.sleep(0.5)
                placed = True
                redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pre_place_position.tolist()))
            elif np.linalg.norm(current_position - pre_place_position) < 0.01 and placed:
                state = State.FINISH

        elif state == State.FINISH:
            print("FINISH")
            print("Pick-and-place task completed.")
            break

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Keyboard interrupted.")
