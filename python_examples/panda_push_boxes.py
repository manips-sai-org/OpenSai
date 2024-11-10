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

        currentPosition = np.array(json.loads(redisClient.get(redisKeys.cartesian_task_current_position)))

        if np.linalg.norm(goalPosition - currentPosition) < 1e-2:
            return
        
        print("Status of {}: {}".format(taskName, i/maxIterations)) 
        

def CheckCartesianController() -> bool:
    return redisClient.get(redisKeys.active_controller).decode("utf-8") == "cartesian_controller"

def CrazyRoutine():
    positionOne = np.array([0, 0.2, 0.4])
    SetCartesianPosition("crazyFirst", positionOne, 500)
    positionTwo = np.array([0.4, 0.4, 0.6])
    SetCartesianPosition("crazySecond", positionTwo, 500)
    positionThree = np.array([0.4, 0.4, 0.4])
    SetCartesianPosition("crazyThird", positionThree, 500)
    pass

def NormalRoutine():
    positionOne = np.array([0.2, 0.2, 0.2])
    SetCartesianPosition("normalFirst", positionOne, 500)
    positionTwo = np.array([0.4, 0.4, 0.4])
    SetCartesianPosition("normalSecond", positionTwo, 500)
    positionThree = np.array([0.5, 0.5, 0.5])
    SetCartesianPosition("normalThird", positionThree, 500)
    pass

def BlockPushRoutine(yOffset: float):
    ResetRoutine()
    lowPosition = np.array([0.37, yOffset, 0.06])
    SetCartesianPosition("blocksweeplow", lowPosition, 500)
    pushPosition = np.array([0.5, yOffset, 0.06])
    SetCartesianPosition("blockpushlow", pushPosition, 500)
    SetCartesianPosition("blocksweeplow", lowPosition, 500)
    ResetRoutine()

def ResetRoutine():
    positionOne = np.array([0.2, 0, 0.4])
    SetCartesianPosition("reset", positionOne, 500)

def MoveAndOrientate(routineOne: str, routineTwo: str):
    pass

def main():

    state = State.FirstPush


    try: 
        while True:
            if state == State.FirstPush:
                BlockPushRoutine(0)
                state = State.SecondPush
            elif state == State.SecondPush:
                BlockPushRoutine(0.5)
                state = State.Normal
            elif state == State.Normal:
                ResetRoutine()

            time.sleep(feedbackTime)

    except KeyboardInterrupt:
        print("Keyboard interrupt")
        pass
    except Exception as e:
        print(e)
        pass

    pass

if __name__ == "__main__":
    main()
