from robot_control import GetDiscreteState
import numpy as np
from robot_control import ObjectiveFunction
from robot_control import StateToNum
from robot_control import NumToState
from robot_control import PickAction
from robot_control import GetExploreRates
from robot_control import NumToAction
from robot_control import ActionToNum


def TestGetDiscreteState():

    basePos = np.array([0.5, 0.5])
    endEff = np.array([0.3,0.4])
    dogPos = np.array([0.7,0.5])

    print(GetDiscreteState(endEff, basePos, dogPos))

    basePos = np.array([0.5, 0.5])
    endEff = np.array([-0.1,0.4])
    dogPos = np.array([0.7,0.5])

    print(GetDiscreteState(endEff, basePos, dogPos))

    basePos = np.array([0.5, 0.5])
    endEff = np.array([0.1, -0.1])
    dogPos = np.array([0.7,0.5])

    print(GetDiscreteState(endEff, basePos, dogPos))


#our modified objective function is now working
def TestObjectiveFunction():

    basePos = np.array([0.35, 0.35])
    endEff = np.array([0.1,-0.1])
    dogPos = np.array([0.7,0.5])

    print(ObjectiveFunction(dogPos, basePos, endEff))

    basePos = np.array([0.3, 0.3])
    endEff = np.array([-0.1,0.4])
    dogPos = np.array([0.7,0.5])

    print(ObjectiveFunction(dogPos, basePos, endEff))

def TestStateToNum():

    r = 0
    dog_close = 0
    dog_side = 0
    opt_side = 0
    opt_dist = 0

    print(StateToNum(r,dog_close, dog_side, opt_side, opt_dist))

    r = 0
    dog_close = 0
    dog_side = 0
    opt_side = 0
    opt_dist = 1

    print(StateToNum(r,dog_close, dog_side, opt_side, opt_dist))

def TestNumToState():

    r = 2
    dog_close = 1
    dog_side = 0
    opt_side = 1
    opt_dist = 0

    num = StateToNum(r,dog_close, dog_side, opt_side, opt_dist)

    state = NumToState(num)

    print("State = {}",format(state))

def TestPickAction():

    q_table = np.random.normal(0, 1, (120, 17))



    PickAction()

def TestExploreRates():

    print(GetExploreRates(95, 0.2, 0.9, 0.1, [0,18,36,54,76,90]))

def TestActions():

    action_nums = [i for i in range(17)]

    print(action_nums)

    actions = []

    for num in action_nums:
        actions.append(NumToAction(num))

    print(actions)

    new_action_nums = []

    for action in actions:
        new_action_nums.append(ActionToNum(action[0], action[1]))

    print(new_action_nums)

def main():

    # TestGetDiscreteState()

    # TestObjectiveFunction()

    # # TestStateToNum()

    # # TestNumToState()

    # TestExploreRates()

    TestActions()

    pass

if __name__ == "__main__":
    main()