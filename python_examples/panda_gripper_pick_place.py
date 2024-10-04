import numpy as np
import time
import json
import redis
import math
from enum import Enum, auto
from dataclasses import dataclass
from scipy.spatial.transform import Rotation as R

DEG_TO_RAD = math.pi / 180.0

class State(Enum):
  INIT = auto()
  PICK = auto()
  PLACE = auto()
  FINISH = auto()


@dataclass
class RedisKeys:
  cartesian_task_goal_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_position"
  cartesian_task_goal_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_orientation"
  cartesian_task_current_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_position"
  cartesian_task_current_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_orientation"
  gripper_task_goal_position: str = "opensai::controller::Panda::cartesian_controller::gripper_fingers::goal_position"
  object_current_position: str = "opensai::simviz::obj_pose::Box"
  active_controller: str = "opensai::controller::Panda::active_controller_name"

redis_keys = RedisKeys()

place_goal_position_left = np.array([0.4, -0.3, 0.225])
place_goal_position_right = np.array([0.45, 0.35, 0.325])

# redis client
redis_client = redis.Redis()

init_position = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_current_position)))
init_orientation = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_current_orientation)))

object_position = np.array(json.loads(redis_client.get(redis_keys.object_current_position)))[0:3,3]
place_goal_position = place_goal_position_left
if object_position[1] < 0:
  place_goal_position = place_goal_position_right

gripper_open_position = np.array([0.04,0.04])
gripper_mid_position = np.array([0.02,0.02])
gripper_closed_position = np.array([0.005,0.005])

pre_pick_position = object_position + np.array([0,0,0.1])
pick_position = object_position
pre_place_position = place_goal_position + np.array([0,0,0.1])
place_position = place_goal_position

picked = False
placed = False

# loop at 100 Hz
loop_time = 0.0
dt = 0.01
internal_step = 0
state = State.INIT

time.sleep(0.01)
init_time = time.perf_counter_ns() * 1e-9

try:
  while True:
    loop_time += dt
    # check the active controller is the cartesian one
    active_controller = redis_client.get(redis_keys.active_controller).decode("utf-8")
    if active_controller != "cartesian_controller":
        print("Exiting, active controller is not cartesian_controller")
        exit(0)
    
    # read robot state
    current_position = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_current_position)))
    current_orientation = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_current_orientation)))

    # state machine
    if state == State.INIT:
      goal_position = pre_pick_position
      goal_orientation = (R.from_matrix(np.array([[1,0,0],[0,-1,0],[0,0,-1]])) * R.from_rotvec(np.array([0,0,45*DEG_TO_RAD]))).as_matrix()
      
      redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(goal_position.tolist()))
      redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(goal_orientation.tolist()))
      redis_client.set(redis_keys.gripper_task_goal_position, json.dumps(gripper_open_position.tolist()))
      state = State.PICK

    if state == State.PICK:
      if np.linalg.norm(current_position - pre_pick_position) < 0.012 and not picked:
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pick_position.tolist()))
      if np.linalg.norm(current_position - pick_position) < 0.012 and not picked:
        redis_client.set(redis_keys.gripper_task_goal_position, json.dumps(gripper_closed_position.tolist()))
        time.sleep(0.5)
        picked = True
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pre_pick_position.tolist()))
      if np.linalg.norm(current_position - pre_pick_position) < 0.012 and picked:
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pre_place_position.tolist()))
        state = State.PLACE
    
    if state == State.PLACE:
      if np.linalg.norm(current_position - pre_place_position) < 0.012 and not placed:
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(place_position.tolist()))
      if np.linalg.norm(current_position - place_position) < 0.012 and not placed:
        redis_client.set(redis_keys.gripper_task_goal_position, json.dumps(gripper_open_position.tolist()))
        time.sleep(0.5)
        placed = True
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(pre_place_position.tolist()))
      if np.linalg.norm(current_position - pre_place_position) < 0.012 and placed:
        state = State.FINISH
        
    if state == State.FINISH:
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(init_position.tolist()))
        redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(init_orientation.tolist()))
        print("Finished")
        exit(0)
        


except KeyboardInterrupt:
  print("Keyboard interrupt")
  pass
except Exception as e:
  print(e)
  pass