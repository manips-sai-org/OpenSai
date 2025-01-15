import json
import numpy as np
import time
import math

#This file contains all of the methods needed in order to control a robot in SAI, 

def CheckCartesianController(redis_client, redis_keys) -> bool:
    return redis_client.get(redis_keys.active_controller).decode("utf-8") == "cartesian_controller"

def SetCartesianPosition(redis_client, redis_keys, robot_origin, goal_pos: np.array, max_iter: int):

    redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(np.subtract(goal_pos, robot_origin).tolist()))

    prev_pos = np.array([0,0,0])
   
    for i in range(max_iter):
        if CheckCartesianController() == False:
            return
        time.sleep(0.01)

        curr_pos = GetCartesianPosition()

        if np.linalg.norm(goal_pos - curr_pos) < 1e-6 or (i > 1 and np.linalg.norm(prev_pos - curr_pos) < 1e-8):
            return

        prev_pos = curr_pos.copy()
        
def SetTask(redis_client, redis_keys, robot_origin, goal_pos: np.array):
    redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(np.subtract(goal_pos, robot_origin).tolist()))

def SetTaskAndBase(redis_client, redis_keys, robot_origin, goal_pos: np.array, max_iter: int, correction: float):

    checkPointPosition = GetCartesianPosition(redis_client, redis_keys, robot_origin)
    distance = np.linalg.norm(goal_pos - checkPointPosition)

    redis_client.set(redis_keys.cartesian_task_goal_position, json.dumps(np.subtract(goal_pos, robot_origin).tolist()))

    prevPosition = np.array([0,0,0])
   
    for i in range(max_iter):
        if CheckCartesianController(redis_client, redis_keys) == False:
            return
        time.sleep(0.01)

        currentPosition = GetCartesianPosition(redis_client, redis_keys, robot_origin)

        if np.linalg.norm(goal_pos - currentPosition) < 1e-2 or (i > 1 and np.linalg.norm(prevPosition - currentPosition) < 1e-5):
            return
        
        if np.linalg.norm(currentPosition - checkPointPosition) > distance/correction:
            print("Setting Base")
            BaseControl(redis_client, redis_keys, robot_origin, 0, 0, 0.6, currentPosition)
            checkPointPosition = currentPosition
    
        prevPosition = currentPosition.copy()

def BaseControl(redis_client, redis_keys , robot_origin, x0: float, y0: float, radius: float, desiredPos: np.array) -> np.array:

    x = desiredPos[0]
    y = desiredPos[1]
    vx = x - x0
    vy = y - y0

    v = np.array([vx, vy])
    norm_v = np.linalg.norm(v)

    if norm_v < 1e-2:
        return
    
    u = v/norm_v
    origin = np.array([x0, y0])
    goalBasePos = origin + radius*u

    SetMobileBasePosition(redis_client, redis_keys, robot_origin, goalBasePos) 

    return goalBasePos

def SetCartesianOrientation(redis_client, redis_keys, goal_orient: np.array):
    redis_client.set(redis_keys.cartesian_task_goal_orientation, json.dumps(goal_orient.tolist()))

        
def GetCartesianPosition(redis_client, redis_keys, robot_origin) -> np.array:
    currentPosition = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_current_position)))
    currentPosition = np.add(currentPosition, robot_origin)

    return currentPosition

def GetCartesianGoalPosition(redis_client, redis_keys, robot_origin) -> np.array:
    goalPosition = np.array(json.loads(redis_client.get(redis_keys.cartesian_task_goal_position)))
    goalPosition = np.add(goalPosition, robot_origin)

    return goalPosition

def GetMobileBasePosition(redis_client, redis_keys, robot_origin) -> np.array:
    currentPosition = np.array(json.loads(redis_client.get(redis_keys.mobile_base_current_position)))
    currentPosition = np.add(currentPosition, robot_origin[:2])

    return currentPosition

def SetMobileBasePosition(redis_client, redis_keys, robot_origin, goalPosition: np.array):
    goalPosition = np.subtract(goalPosition, robot_origin[:2])
    redis_client.set(redis_keys.mobile_base_goal_position, json.dumps(goalPosition.tolist()))

def SetMobileBaseVel(redis_client, redis_keys, vel: np.array):
    redis_client.set(redis_keys.mobile_base_vel_otg, json.dumps(vel.tolist()))

def SetMobileBaseAcc(redis_client, redis_keys, acc: np.array):
    redis_client.set(redis_keys.mobile_base_acc_otg, json.dumps(acc.tolist()))

def MoveToStart(redis_client, redis_keys, robot_origin, start_pos: np.array):

    goal_base_pos = SetTaskAndBase(redis_client, redis_keys, robot_origin, start_pos, 500, 50)
    time.sleep(1.5)

def MoveToEnd(redis_client, redis_keys, robot_origin, end_pos: np.array, fast = False):
    SetTask(redis_client, redis_keys, robot_origin, end_pos)

    #Set otg to some value - optional
    # SetMobileBaseVel(redis_client, redis_keys, np.array([0.5]))

    goal_base_pos = SetTaskAndBase(redis_client, redis_keys, robot_origin, end_pos, 500, 50)
    time.sleep(1.5)

def GetBaseAngle(redis_client, redis_keys, robot_origin): 

    base_pos = GetMobileBasePosition(redis_client, redis_keys, robot_origin)
    base_angle = math.atan2(base_pos[1], base_pos[0])

    if base_angle < 0:
        base_angle += 2 * math.pi

    return base_angle

def InchBase(redis_client, redis_keys, robot_origin, radius, increment, direction):

    base_angle = GetBaseAngle(redis_client, redis_keys, robot_origin)
    signed_increment = increment * direction
    target = np.array([radius * math.cos(base_angle + signed_increment), radius * math.sin(base_angle + signed_increment)])

    SetMobileBasePosition(redis_client, redis_keys, robot_origin , target)

    return target

def ResetRobot(redis_client, redis_keys):
    time.sleep(1)
    redis_client.set(redis_keys.reset, json.dumps(1))
    time.sleep(1)

    

