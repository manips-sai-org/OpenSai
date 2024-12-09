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
    GOING_ABOVE_OBJECT = auto()
    GOING_TO_OBJECT = auto()
    MOVE_OBJECT = auto()
    END = auto()


@dataclass
class RedisKeys:
    kuka_goal_position: str = "opensai::controllers::Kuka::eef_control::eef_task::goal_position"
    kuka_goal_orientation: str = "opensai::controllers::Kuka::eef_control::eef_task::goal_orientation"
    kuka_current_position: str = "opensai::controllers::Kuka::eef_control::eef_task::current_position"
    kuka_current_orientation: str = "opensai::controllers::Kuka::eef_control::eef_task::current_orientation"
    kuka_sensed_force: str = "opensai::controllers::Kuka::eef_control::eef_task::sensed_force"
    kuka_desired_force: str = "opensai::controllers::Kuka::eef_control::eef_task::desired_force"
    kuka_force_space_dimension: str = "opensai::controllers::Kuka::eef_control::eef_task::force_space_dimension"
    kuka_force_space_axis: str = "opensai::controllers::Kuka::eef_control::eef_task::force_space_axis"
    config_file_name: str = "::sai-interfaces-webui::config_file_name"
    object_pose = "opensai::sensors::Object::object_pose"

redis_keys = RedisKeys()

config_file_for_this_example = "kuka_object_friction.xml"

init_goal_pos = np.array([0.6, 0.0, 0.575])
init_goal_ori = np.array([[-1.0, 0, 0], [0, 1.0, 0], [0, 0, -1.0]])

goal_pos = init_goal_pos
goal_ori = init_goal_ori

table_goal_angles = np.array([0.0, 0.0])

# redis client
redis_client = redis.Redis()

# check that the config file is correct
config_file_name = redis_client.get(
    redis_keys.config_file_name).decode("utf-8")
if config_file_name != config_file_for_this_example:
    print("This example is meant to be used with the config file: ",
          config_file_for_this_example)
    exit(0)

# set the initial goal position and orientation
redis_client.set(redis_keys.kuka_goal_position,
                 json.dumps(goal_pos.tolist()))
redis_client.set(redis_keys.kuka_goal_orientation,
                 json.dumps(init_goal_ori.tolist()))

# loop at 100 Hz
loop_time = 0.0
dt = 0.01
state = State.INIT

time.sleep(0.01)
init_time = time.perf_counter_ns() * 1e-9

try:
    while True:
        loop_time += dt
        time.sleep(
            max(0, loop_time - (time.perf_counter_ns() * 1e-9 - init_time)))

        # read robot state
        current_position = np.array(
            json.loads(redis_client.get(redis_keys.kuka_current_position)))
        current_orientation = np.array(
            json.loads(redis_client.get(redis_keys.kuka_current_orientation)))

        # state machine
        if state == State.INIT:
            # monitor error
            pos_error = np.linalg.norm(goal_pos - current_position)
            ori_error = np.linalg.norm(goal_ori - current_orientation)
            if pos_error < 1e-2 and ori_error < 1e-2:
                object_position = np.array(json.loads(redis_client.get(redis_keys.object_pose)))[0:3,3]
                goal_pos = object_position + np.array([0, 0, 0.1])
                redis_client.set(redis_keys.kuka_goal_position,
                                 json.dumps(goal_pos.tolist()))
                state = State.GOING_ABOVE_OBJECT
                print("Going above object")

        elif state == State.GOING_ABOVE_OBJECT:
            pos_error = np.linalg.norm(goal_pos - current_position)
            if(pos_error < 1e-2):
                goal_pos = current_position - np.array([0, 0, 0.15])
                redis_client.set(redis_keys.kuka_goal_position,
                                 json.dumps(goal_pos.tolist()))
                state = State.GOING_TO_OBJECT
                print("Going to object")
            
        elif state == State.GOING_TO_OBJECT:
            # monitor contact force
            sensed_force = np.array(
                json.loads(redis_client.get(redis_keys.kuka_sensed_force)))
            if sensed_force[2] < -12.0:
                # parametrize force space and moment space
                redis_client.set(redis_keys.kuka_force_space_dimension, "1")
                redis_client.set(redis_keys.kuka_force_space_axis,
                                 json.dumps([0, 0, 1]))
                redis_client.set(redis_keys.kuka_desired_force, json.dumps([0, 0, -12]))

                # wait more than 2 controller cycles to let the inputs reset after force control reparametrization
                time.sleep(0.002)

                # move object towards the robot in the x direction
                goal_pos = current_position - np.array([0.1, 0, 0])
                redis_client.set(redis_keys.kuka_goal_position,
                                 json.dumps(goal_pos.tolist()))

                state = State.MOVE_OBJECT
                print("Move object")

        elif state == State.MOVE_OBJECT:
            pos_error = np.linalg.norm(goal_pos[0:2] - current_position[0:2])
            if(pos_error < 1e-3):
                redis_client.set(redis_keys.kuka_force_space_dimension, "0")
                
                # wait more than 2 controller cycles to let the inputs reset after force control reparametrization
                time.sleep(0.002)
                
                redis_client.set(redis_keys.kuka_goal_position,
                                 json.dumps(init_goal_pos.tolist()))
                state = State.END
                print("Return to initial position")
            

        elif state == State.END:
            print("Exit state machine")
            exit(0)

except KeyboardInterrupt:
    print("Keyboard interrupt")
    pass
except Exception as e:
    print(e)
    pass
