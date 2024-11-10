import numpy as np
import time
import json
import redis
import math
from enum import Enum, auto
from dataclasses import dataclass

@dataclass
class RedisKeys:
    cartesian_task_goal_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_position"
    cartesian_task_goal_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::goal_orientation"
    cartesian_task_current_position: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_position"
    cartesian_task_current_orientation: str = "opensai::controller::Panda::cartesian_controller::cartesian_task::current_orientation"
    active_controller: str = "opensai::controller::Panda::active_controller_name"

#ok we are only concerned with cartesian position and orientation
redisKeys = RedisKeys()
feedbackTime = 0.01

class State(Enum):
    Crazy = auto()
    Normal = auto()
    FirstPush = auto()
    SecondPush = auto()

redisKeys = RedisKeys()
redisClient = redis.Redis()

#Let us assume that the redisClient is a redis client that is able to set, get, etc from the redis database
#goal position is a numpy array

#Let us implement stagnancy beater - time based and position based
    
def SetCartesianPosition(taskName: str, goalPosition: np.array, maxIterations: int):
    redisClient.set(redisKeys.cartesian_task_goal_position, json.dumps(goalPosition.tolist()))
    for i in range(maxIterations):
        if CheckCartesianController() == False:
            return
        time.sleep(feedbackTime)

        currentPosition = GetCartesianPosition()

        if np.linalg.norm(goalPosition - currentPosition) < 1e-2:
            return
        
        print("Status of {}: {}".format(taskName, i/maxIterations)) 

def GetCartesianPosition() -> np.array:
    currentPosition = np.array(json.loads(redisClient.get(redisKeys.cartesian_task_current_position)))

    return currentPosition
        

def CheckCartesianController() -> bool:
    return redisClient.get(redisKeys.active_controller).decode("utf-8") == "cartesian_controller"

#Assume that there is non degenerate input, valid start location, etc
#create an algorithm that solves a maze
def FindShortestPath(grid: list[list[str]], startLocation: tuple[int, int]) -> list[tuple[int, int]]:

    optimalPath = []
    
    #Lets generate a list that contains the explored values 2d grid of the DFS, this will also store the optimal path
    exploreMap = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]

    #Run the BFS algorithm here, and mark the previous point as a vector

    bfsQueue = []

    bfsQueue.append((startLocation))
    exploreMap[startLocation[0]][startLocation[1]] = (-1,-1)

    finalPosition = (-1,-1)

    while len(bfsQueue) > 0:

        currentPosition = bfsQueue.pop(0)

        if grid[currentPosition[0]][currentPosition[1]] == "d":
            finalPosition = currentPosition
            break

        if currentPosition[1] + 1 < gridWidth and exploreMap[currentPosition[0]][currentPosition[1] +1] == (-1,-1) and grid[currentPosition[0]][currentPosition[1] +1] != "x":
            right = (currentPosition[0], currentPosition[1]+1)
            exploreMap[right[0]][right[1]] = (currentPosition[0], currentPosition[1])
            bfsQueue.append(right)
        if currentPosition[1] -1 >= 0 and exploreMap[currentPosition[0]][currentPosition[1] -1] == (-1,-1) and grid[currentPosition[0]][currentPosition[1] -1] != "x":
            left = (currentPosition[0], currentPosition[1]-1)
            exploreMap[left[0]][left[1]] = (currentPosition[0], currentPosition[1])
            bfsQueue.append(left)
        if currentPosition[0] +1 < gridHeight and exploreMap[currentPosition[0] + 1][currentPosition[1]] == (-1,-1) and grid[currentPosition[0] + 1][currentPosition[1]] != "x":
            down = (currentPosition[0] + 1, currentPosition[1])
            exploreMap[down[0]][down[1]] = (currentPosition[0], currentPosition[1])
            bfsQueue.append(down)
        if currentPosition[0] -1 >= 0 and exploreMap[currentPosition[0] -1][currentPosition[1]] == (-1,-1) and grid[currentPosition[0] - 1][currentPosition[1]] != "x":
            up = (currentPosition[0] -1, currentPosition[1])
            exploreMap[up[0]][up[1]] = (currentPosition[0], currentPosition[1])
            bfsQueue.append(up)

    if finalPosition == (-1, -1):
        print("Final position was not updated!")
        return optimalPath

    
    currPosition = finalPosition
    while currPosition != startLocation:
        optimalPath.append(currPosition)
        currPosition = exploreMap[currPosition[0]][currPosition[1]]

    optimalPath.append(startLocation)

    return optimalPath

def MoveRobot(optimalPath: list[tuple[int,int]], delta: float):

    ResetPosition()

    for i in range(0, len(optimalPath) -1):
        j = len(optimalPath) -1 - i
        dx = float(optimalPath[j-1][1] - optimalPath[j][1])*delta
        dy = float(optimalPath[j-1][0] - optimalPath[j][0]) * delta

        taskName = "movement-{}".format(i)

        currentPosition = GetCartesianPosition()
        goalPosition = np.add(currentPosition, np.array([dy, dx, 0]))
        SetCartesianPosition(taskName=taskName, goalPosition=goalPosition, maxIterations=500)


    pass


def ResetPosition():
    taskName = "reset"
    SetCartesianPosition(taskName=taskName, goalPosition = np.array([0,0,0.5]), maxIterations=500)

def main():

    #Let us do some unit testing to see if the optimal path program/ instructions works

    grid1 = [["", "", "x", "", "", "", "x", "d"],
            ["x", "", "x", "", "x", "", "x", ""], 
            ["x", "", "x", "", "x", "", "x", ""],
            ["x", "", "x", "", "x", "", "x", ""],
            ["x", "", "x", "", "x", "", "x", ""],
            ["x", "", "x", "", "x", "", "x", ""],
            ["x", "", "x", "", "x", "", "x", ""],
            ["x", "", "", "", "x", "", "", ""]]
    
    startLocation1 = (0,0)

    optimalPath = FindShortestPath(grid= grid1, startLocation = startLocation1)

    print(optimalPath)

    MoveRobot(optimalPath= optimalPath, delta = 0.1)

if __name__ == "__main__":
    main()
