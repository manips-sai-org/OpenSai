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
    GOING_TO_CONTACT = auto()
    SURFACE_ALIGNMENT = auto()


@dataclass
class RedisKeys:
    kuka_goal_position: str = "opensai::controllers::Kuka::eef_control::eef_task::goal_position"
    kuka_goal_orientation: str = "opensai::controllers::Kuka::eef_control::eef_task::goal_orientation"
    kuka_current_position: str = "opensai::controllers::Kuka::eef_control::eef_task::current_position"
    kuka_current_orientation: str = "opensai::controllers::Kuka::eef_control::eef_task::current_orientation"
    kuka_sensed_force: str = "opensai::controllers::Kuka::eef_control::eef_task::sensed_force"
    kuka_desired_force: str = "opensai::controllers::Kuka::eef_control::eef_task::desired_force"
    kuka_desired_moment: str = "opensai::controllers::Kuka::eef_control::eef_task::desired_moment"
    kuka_force_space_dimension: str = "opensai::controllers::Kuka::eef_control::eef_task::force_space_dimension"
    kuka_moment_space_dimension: str = "opensai::controllers::Kuka::eef_control::eef_task::moment_space_dimension"
    kuka_force_space_axis: str = "opensai::controllers::Kuka::eef_control::eef_task::force_space_axis"
    kuka_moment_space_axis: str = "opensai::controllers::Kuka::eef_control::eef_task::moment_space_axis"
    kuka_closed_loop_force_control: str = "opensai::controllers::Kuka::eef_control::eef_task::closed_loop_force_control"
    kuka_otg_enabled: str = "opensai::controllers::Kuka::eef_control::eef_task::otg_enabled"
    config_file_name: str = "::sai2-interfaces-webui::config_file_name"
    table_goal_angles: str = "opensai::controllers::Table::tilt_controller::tilt_task::goal_position"


redis_keys = RedisKeys()

config_file_for_this_example = "kuka_plate_table.xml"

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
                 json.dumps(init_goal_pos.tolist()))
redis_client.set(redis_keys.kuka_goal_orientation,
                 json.dumps(init_goal_ori.tolist()))

# loop at 100 Hz
loop_time = 0.0
dt = 0.01
loop_step = 0
state = State.INIT

time.sleep(0.01)
init_time = time.perf_counter_ns() * 1e-9

try:
    while True:
        loop_time += dt
        time.sleep(
            max(0, loop_time - (time.perf_counter_ns() * 1e-9 - init_time)))

        # table tilt control
        if (loop_step % 1000) == 0:
            table_goal_angles[0] = 12.0 * DEG_TO_RAD
        if (loop_step % 1000) == 500:
            table_goal_angles[0] = -12.0 * DEG_TO_RAD
        if (loop_step % 1500) == 0:
            table_goal_angles[1] = 18.0 * DEG_TO_RAD
        if (loop_step % 1500) == 750:
            table_goal_angles[1] = -18.0 * DEG_TO_RAD

        redis_client.set(redis_keys.table_goal_angles,
                         json.dumps(table_goal_angles.tolist()))

        # read robot state
        current_position = np.array(
            json.loads(redis_client.get(redis_keys.kuka_current_position)))
        current_orientation = np.array(
            json.loads(redis_client.get(redis_keys.kuka_current_orientation)))

        # state machine
        if state == State.INIT:
            # monitor error
            pos_error = np.linalg.norm(init_goal_pos - current_position)
            ori_error = np.linalg.norm(init_goal_ori - current_orientation)
            if pos_error < 1e-2 and ori_error < 1e-2:
                contact_goal_position = init_goal_pos - np.array([0, 0, 0.4])
                redis_client.set(redis_keys.kuka_goal_position,
                                 json.dumps(contact_goal_position.tolist()))
                state = State.GOING_TO_CONTACT
                print("Going to contact")

        elif state == State.GOING_TO_CONTACT:
            # monitor contact force
            sensed_force = np.array(
                json.loads(redis_client.get(redis_keys.kuka_sensed_force)))
            if sensed_force[2] < -15.0:
                # parametrize force space and moment space
                redis_client.set(redis_keys.kuka_force_space_dimension, "1")
                redis_client.set(redis_keys.kuka_force_space_axis,
                                 json.dumps([0, 0, 1]))
                redis_client.set(redis_keys.kuka_moment_space_dimension, "2")
                redis_client.set(redis_keys.kuka_moment_space_axis,
                                 json.dumps([0, 0, 1]))
                redis_client.set(redis_keys.kuka_closed_loop_force_control, "1")

                redis_client.set(redis_keys.kuka_otg_enabled, "0")

                state = State.SURFACE_ALIGNMENT
                print("Surface alignment")

        elif state == State.SURFACE_ALIGNMENT:
            # send the force and moment goals
            redis_client.set(redis_keys.kuka_desired_force,
                             json.dumps([0, 0, -15.0]))
            redis_client.set(redis_keys.kuka_desired_moment,
                             json.dumps([0, 0, 0]))

        loop_step += 1

except KeyboardInterrupt:
    print("Keyboard interrupt")
    pass
except Exception as e:
    print(e)
    pass
