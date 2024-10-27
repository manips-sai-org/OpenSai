import numpy as np
import time
import json
import redis
import math
from enum import Enum, auto
from dataclasses import dataclass

DEG_TO_RAD = math.pi / 180.0

class State(Enum):
  INIT = auto()
  GOING_LEFT = auto()
  GOING_RIGHT = auto()


@dataclass
class RedisKeys:
  cartesian_task_goal_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_position"
  cartesian_task_goal_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_orientation"
  cartesian_task_current_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_position"
  cartesian_task_current_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_orientation"
  active_controller: str = "opensai::controller::Panda::active_controller_name"

redis_keys = RedisKeys()


rot_y_15_deg = np.array([[math.cos(15.0 * DEG_TO_RAD), 0, -math.sin(15.0 * DEG_TO_RAD)],
                         [0, 1, 0],
                         [math.sin(15.0 * DEG_TO_RAD), 0, math.cos(15.0 * DEG_TO_RAD)]])
rot_x_30_deg = np.array([[1, 0, 0],
                         [0, math.cos(30.0 * DEG_TO_RAD), -math.sin(30.0 * DEG_TO_RAD)],
                         [0, math.sin(30.0 * DEG_TO_RAD), math.cos(30.0 * DEG_TO_RAD)]])

init_goal_pos = np.array([0.55, 0.0, 0.50])
init_goal_ori = np.dot(np.array([[1.0,0,0],[0,-1.0,0],[0,0,-1.0]]),rot_y_15_deg.T)

left_goal_pos = init_goal_pos - np.array([0, 0.2, 0])
right_goal_pos = init_goal_pos + np.array([0, 0.2, 0])
left_goal_ori = np.dot(init_goal_ori, rot_x_30_deg.T)
right_goal_ori = np.dot(init_goal_ori, rot_x_30_deg)

goal_pos = init_goal_pos
goal_ori = init_goal_ori

# redis client
redis_client = redis.Redis()

redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(init_goal_pos.tolist()))
redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(init_goal_ori.tolist()))

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
      # monitor error
      pos_error = np.linalg.norm(init_goal_pos - current_position)
      ori_error = np.linalg.norm(init_goal_ori - current_orientation)
      if pos_error < 1e-2 and ori_error < 1e-2:
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(left_goal_pos.tolist()))
        redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(left_goal_ori.tolist()))
        state = State.GOING_LEFT
        print("Going Left")

    elif state == State.GOING_LEFT:
      # monitor error
      pos_error = np.linalg.norm(left_goal_pos - current_position)
      ori_error = np.linalg.norm(left_goal_ori - current_orientation)
      if pos_error < 1e-2 and ori_error < 1e-2:
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(right_goal_pos.tolist()))
        redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(right_goal_ori.tolist()))
        state = State.GOING_RIGHT
        print("Going Right")

    elif state == State.GOING_RIGHT:
      # monitor error
      pos_error = np.linalg.norm(right_goal_pos - current_position)
      ori_error = np.linalg.norm(right_goal_ori - current_orientation)
      if pos_error < 1e-2 and ori_error < 1e-2:
        redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(left_goal_pos.tolist()))
        redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(left_goal_ori.tolist()))
        state = State.GOING_LEFT
        print("Going Left")

except KeyboardInterrupt:
  print("Keyboard interrupt")
  pass
except Exception as e:
  print(e)
  pass