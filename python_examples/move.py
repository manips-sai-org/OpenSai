import numpy as np
import time
import json
import math
from enum import Enum, auto
from dataclasses import dataclass
from scipy.spatial.transform import Rotation as R
import sys
import os
import yaml
import redis

dt = 0.01
robotOrigin = np.array([0,0,0])
fD = 0.6
correctionFactor = 0.0001
table_x = 0
table_y = 0
gripper_open_position = np.array([0.04,0.04])
gripper_mid_position = np.array([0.02,0.02])
gripper_closed_position = np.array([0.003,0.003])
DEG_TO_RAD = math.pi / 180.0

@dataclass
class RedisKeys:
    cartesian_task_goal_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_position"
    cartesian_task_goal_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_orientation"
    cartesian_task_current_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_position"
    mobile_base_current_position: str = "opensai::controller::Panda::cartesian_controller::mobile_base::current_position"
    mobile_base_goal_position: str = "opensai::controller::Panda::cartesian_controller::mobile_base::goal_position"
    cartesian_task_current_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_orientation"
    active_controller: str = "opensai::controller::Panda::active_controller_name"
    piece_current_position: str = "opensai::simviz::obj_pose::piece"
    gripper_task_goal_position: str = "opensai::controller::Panda::cartesian_controller::gripper_fingers::goal_position"

redisKeys = RedisKeys()
redisClient = redis.Redis()

def SetCartesianPosition(taskName: str, goalPosition: np.array, maxIterations: int, telemetry: bool):

    redisClient.set(redisKeys.cartesian_task_goal_position, json.dumps(np.subtract(goalPosition, robotOrigin).tolist()))

    prevPosition = np.array([0,0,0])
   
    for i in range(maxIterations):
        if CheckCartesianController() == False:
            return
        time.sleep(dt)

        currentPosition = GetCartesianPosition()

        if np.linalg.norm(goalPosition - currentPosition) < 1e-6 or (i > 1 and np.linalg.norm(prevPosition - currentPosition) < 1e-8):
            return

        prevPosition = currentPosition.copy()
        
        if telemetry:
            print("Telemetry: {}, iter: {}, distanceFromTask: {}".format(taskName, i, np.linalg.norm(goalPosition - currentPosition)))

#Apply base control will be an integer n, for every 1/n progress made by task control
#This correction factor distance/correction can be set to a constant as well
def SetTaskAndBase(goalPosition: np.array, maxIterations: int, correction: float):

    checkPointPosition = GetCartesianPosition()
    distance = np.linalg.norm(goalPosition - checkPointPosition)

    redisClient.set(redisKeys.cartesian_task_goal_position, json.dumps(np.subtract(goalPosition, robotOrigin).tolist()))

    prevPosition = np.array([0,0,0])
   
    for i in range(maxIterations):
        if CheckCartesianController() == False:
            return
        time.sleep(dt)

        currentPosition = GetCartesianPosition()

        if np.linalg.norm(goalPosition - currentPosition) < 1e-2 or (i > 1 and np.linalg.norm(prevPosition - currentPosition) < 1e-5):
            return
        
        if np.linalg.norm(currentPosition - checkPointPosition) > distance/correction:
            BaseControl(table_x, table_y, 0.6, currentPosition)
            checkPointPosition = currentPosition
        

        prevPosition = currentPosition.copy()
        
        

def SetCartesianOrientation(goalOrientation: np.array):
    redisClient.set(redisKeys.cartesian_task_goal_orientation, json.dumps(goalOrientation.tolist()))

        
def GetCartesianPosition() -> np.array:
    currentPosition = np.array(json.loads(redisClient.get(redisKeys.cartesian_task_current_position)))
    currentPosition = np.add(currentPosition, robotOrigin)

    return currentPosition

def GetCartesianGoalPosition() -> np.array:
    goalPosition = np.array(json.loads(redisClient.get(redisKeys.cartesian_task_goal_position)))
    goalPosition = np.add(goalPosition, robotOrigin)

    return goalPosition

def GetMobileBasePosition() -> np.array:
    currentPosition = np.array(json.loads(redisClient.get(redisKeys.mobile_base_current_position)))
    currentPosition = np.add(currentPosition, robotOrigin)

    return currentPosition

def SetMobileBasePosition(goalPosition: np.array):
    goalPosition = np.subtract(goalPosition, robotOrigin[:2])
    redisClient.set(redisKeys.mobile_base_goal_position, json.dumps(goalPosition.tolist()))

def SetGripperPosition(goalPosition: np.array):
    redisClient.set(redisKeys.gripper_task_goal_position, json.dumps(goalPosition.tolist()))

def getPiecePos() -> np.array:
    return np.array(json.loads(redisClient.get(redisKeys.piece_current_position)))[0:3,3]

def CheckCartesianController() -> bool:
    return redisClient.get(redisKeys.active_controller).decode("utf-8") == "cartesian_controller"

def FindShortestPath(grid: list[list[str]], start: tuple[int, int]) -> list[str]:

    optimalPath = [] # list of up down left right

    explore = [["" for _ in range(len(grid[0]))] for _ in range(len(grid))]

    bfs = []
    bfs.append(start)

    final = (-1,-1)

    while len(bfs) > 0:

        r, c = bfs.pop()

        if grid[r][c] == "d":
            final = (r,c)
            break

        if r + 1 < len(grid) and explore[r+1][c] == "" and grid[r+1][c] != "x":
            explore[r+1][c] = "down"
            bfs.append((r+1, c))

        if r - 1 >= 0 and explore[r-1][c] == "" and grid[r-1][c] != "x":
            explore[r-1][c] = "up"
            bfs.append((r-1, c))

        if c+1 < len(grid[0]) and explore[r][c+1] == "" and grid[r][c+1] != "x":
            explore[r][c+1] = "right"
            bfs.append((r, c+1))

        if c - 1 >= 0 and explore[r][c-1] == "" and grid[r][c-1] != "x":
            explore[r][c-1] = "left"
            bfs.append((r, c-1))

    if final == (-1,-1):
        return optimalPath
    
    row, col = final

    while (row, col) != start:
        if explore[row][col] == "down":
            row = row -1
            optimalPath.insert(0,"down")
        elif explore[row][col] == "up":
            row = row +1
            optimalPath.insert(0, "up")
        elif explore[row][col] == "left":
            col = col +1
            optimalPath.insert(0, "left")
        elif explore[row][col] == "right":
            col = col -1
            optimalPath.insert(0, "right")

    return optimalPath

def CompressOptimalPath(optimalPath: list[str], distance: int) ->  list[str]:

    runningCount = 1
    compressedList = []
    direction = "left"

    for i in range(len(optimalPath) -1):

        direction = optimalPath[i]

        if runningCount == distance:
            compressedList.append((direction, distance))
            runningCount = 1
        elif optimalPath[i] == optimalPath[i+1]:
            runningCount += 1
        else:
            compressedList.append((direction, runningCount))
            runningCount = 1

    

    compressedList.append((optimalPath[-1], runningCount))

    return compressedList


#look for a piece and orient the robot in such a way that grips it
def GripPiece():

    piecePos = getPiecePos()

    desiredPos = piecePos.copy()
    desiredPos[2] += 0.1

    BaseControl(table_x, table_y, 0.6, desiredPos)
    SetCartesianPosition("Moving to Piece", desiredPos, 300, True)

    #open the gripper and grip
    # SetGripperPosition(gripper_open_position)

    desiredPos[2] -= 0.075
    SetCartesianPosition("Moving to Piece", desiredPos, 300, True)

    # SetGripperPosition(gripper_closed_position)
    time.sleep(2)
    desiredPos[2] += 0.02
    SetCartesianPosition("Moving to Piece", desiredPos, 300, True)
    time.sleep(0.5)


def ResetPosition():
    taskName = "reset"
    goal_orientation = (R.from_matrix(np.array([[1,0,0],[0,-1,0],[0,0,-1]])) * R.from_rotvec(np.array([0,0,45*DEG_TO_RAD]))).as_matrix()
    SetCartesianOrientation(goal_orientation)
    SetGripperPosition(gripper_open_position)
    SetCartesianPosition(taskName, np.array([-1,-1,0.5]), 300, True)

#Assumes that the piece is in the starting position
def SolveMaze(mazePos: tuple[float, float, float], mazeScale: tuple[float, float, float], start: tuple[int, int], optimalPath: list[str], compression: int, correction: int):

    optimalPath = CompressOptimalPath(optimalPath, compression)

    dx = mazeScale[0]
    dy = mazeScale[1]

    currPos = GetCartesianPosition()

    for tup in optimalPath:

        dir = tup[0]
        steps = tup[1]

        if dir == "left":
            currPos[1] = currPos[1] - steps * dy
            # BaseControl(table_x, table_y, 0.6, currPos)
            # SetCartesianPosition("moveLeft", currPos, 300, True)
            SetTaskAndBase(currPos, 300, correction)
        elif dir == "right":
            currPos[1] = currPos[1] + steps* dy
            # BaseControl(table_x, table_y, 0.6, currPos)
            # SetCartesianPosition("moveRight", currPos, 300, True)
            SetTaskAndBase(currPos, 300, correction)
        elif dir == "up":
            currPos[0] = currPos[0] - steps* dx
            # BaseControl(table_x, table_y, 0.6, currPos)
            # SetCartesianPosition("moveUp", currPos, 300, True)
            SetTaskAndBase(currPos, 300, correction)
        elif dir == "down":
            currPos[0] = currPos[0] + steps * dx
            # BaseControl(table_x, table_y, 0.6, currPos)
            # SetCartesianPosition("moveDown", currPos, 300, True)
            SetTaskAndBase(currPos, 300, correction)

def PlacePiece():
    currPos = GetCartesianPosition()

    currPos[2] -= 0.2

    SetCartesianPosition("Placing Piece", currPos, 300, False)

    SetGripperPosition(gripper_open_position)

    currPos += 0.2

    SetCartesianPosition("Reset-2", currPos, 300, False)





#what base control does is it sees the task control set, and computes a point to move the base too
#This is a pretty interesting behavior
#There are some flaws with this algorithm like cutting, but having small dx's may be helpful to avoid cutting
#going in and out of the robot origin frame of reference
def BaseControl(x0: float, y0: float, radius: float, desiredPos: np.array):

    #Task position is defined to be within a circle, and base control is a radius outside the circle
    #everything should be parametric, which should in theory be really sick

    x = desiredPos[0]
    y = desiredPos[1]
    vx = x - x0
    vy = y - y0

    #normalize the vector

    v = np.array([vx, vy])
    norm_v = np.linalg.norm(v)

    if norm_v < 1e-2:
        return
    
    u = v/norm_v
    origin = np.array([x0, y0])
    goalBasePos = origin + radius*u

    SetMobileBasePosition(goalBasePos)

def main():

    data = {}

    with open("mazecfg.yaml", "r") as file:
        data = yaml.safe_load(file)

    
    #get all initial data required to move robot from config file
    grid = data['maze']
    r_o = data['robotOrigin']
    r_o.append(0)

    print("r_o is {}".format(r_o))

    global robotOrigin
    robotOrigin = np.array(r_o)

    mazePos = data['mazePos']
    mazeScale = data['mazeScale']

    optimalPath  = FindShortestPath(grid, (0,1))

    ResetPosition()
    GripPiece()
    SolveMaze(mazePos, mazeScale, (0,1), optimalPath, 10, 50)
    # PlacePiece()



if __name__ == "__main__":
    main()

#Footnotes:

# all the positions, get positions and set positions are standardized to be in the world origin frame

#The set position will actually do the coordinate change

#now I just need to implement continuous movement

#I need to write a continuos control algorithm          


#ok so the algorithm will be
#set the set the task control of the robot, periodically poll the robots positition and check its progress
#save an initial position vector

#save the robots position initially, compute the total distance needed to move

#if the norm(currPos - savedPos) > distance/n

#savedPos = currPos
#run Base Control with the current position