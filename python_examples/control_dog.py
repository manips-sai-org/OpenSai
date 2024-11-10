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
import random

@dataclass
class RedisKeys:
    dog_current_position: str = "opensai::controller::Dog::joint_controller::joint_task::current_position"
    dog_goal_position: str = "opensai::controller::Dog::joint_controller::joint_task::goal_position"

redisKeys = RedisKeys()
redisClient = redis.Redis()

dogOrigin = np.array([0,0,0])

def SetDogPosition(goalPosition: np.array):
    goalPosition = np.subtract(goalPosition, dogOrigin[:2])
    redisClient.set(redisKeys.dog_goal_position, json.dumps(goalPosition.tolist()))

def GetDogPosition() -> np.array:
    currentPosition = np.array(json.loads(redisClient.get(redisKeys.dog_current_position)))
    currentPosition = np.add(currentPosition, dogOrigin[:2])
    return currentPosition

#r1 is the short radius, r2 is the large radius
def ControlDog(r1: float, r2: float, step: float):

    #assume that the dog's origin is in between r1 and r2

    for i in range(0, 1000000):

        currPos = GetDogPosition()

        #generate a random angle, go in that angle step distance

        angle = random.random() * 2*math.pi

        print("angle = {}".format(angle))

        x = np.array([math.cos(angle), math.sin(angle)])*step

        targetPos = np.add(currPos, x)

        if np.linalg.norm(targetPos) < r1 or np.linalg.norm(targetPos) > r2:
            print("continued..")
            continue

        SetDogPosition(targetPos)

        print("Dog Position: {}".format(GetDogPosition()))
        time.sleep(0.2)

def main():

    #Read the config file to get the origin of the dog, and 

    with open("mazecfg.yaml", "r") as file:
        data = yaml.safe_load(file)

    d_o = data['dogOrigin']

    global dogOrigin
    dogOrigin = np.array(d_o)

    # SetDogPosition(np.array([0.5,0.5]))
    ControlDog(0.5, 1.0, 0.7)

    pass

if __name__ == "__main__":
    main()