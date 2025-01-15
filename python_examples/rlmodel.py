#This is the RL model interface

from abc import ABC, abstractmethod
from rlkeys import RedisKeys
import redis
import numpy as np
import random 
import math
from math import fmod
import time
from robot_control import GetMobileBasePosition
from robot_control import GetCartesianPosition
from robot_control import SetMobileBaseVel
from robot_control import SetMobileBaseAcc
from robot_control import SetMobileBasePosition
from robot_control import SetTask
from robot_control import GetBaseAngle
from robot_control import InchBase


class RLModel(ABC):

    # @abstractmethod
    # def getObjectiveLoss(self): 
    #     pass

    @abstractmethod
    def pickAction(self):
        pass

    @abstractmethod
    def performAction(self):
        pass

    @abstractmethod
    def getState(self):
         pass
    
    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def eval(self):
        pass

    #Get mode indicates whether the model is in training or eval mode
    @abstractmethod
    def getMode(self):
        pass

    @abstractmethod
    def eval_mode(self):
        pass

    @abstractmethod
    def train_mode(self):
        pass

    @abstractmethod
    def save(self, save_path):
        pass

    @abstractmethod
    def load(self, weights_path):
        pass

class BaseMazeModel(RLModel):

    def __init__(self , redis_client, redis_keys, learning_params, robot_origin, goal_base_pos, maze_scale, num_states, num_actions, weights= None):
        self.Q_TABLE = np.zeros((num_states, num_actions))
        self.num_states = num_states
        self.num_actions = num_actions

        if weights != None:
            self.load(weights)

        self.redis_client = redis_client
        self.redis_keys = redis_keys
        self.learn_freq = learning_params["lfreq"]
        self.lr = learning_params["lr"]
        self.discount = learning_params["discount"]
        self.episode_len = learning_params["episode_len"]
        self.r_o = robot_origin
        self.GOAL_POS = goal_base_pos
        self.m_x = maze_scale[0]
        self.m_y = maze_scale[1]

        self.TARGET_ITER = 300
        self.BASE_ITER = 20

        self.path_index = 0
        self.target = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)
        
        self.mode = "TRAIN"

    def SolveMaze(self, optimalPath):

        tup = optimalPath[self.path_index]
        print(self.path_index)
        dir = tup[0]
        steps = tup[1]

        if dir == "left":
            self.target[1] = self.target[1] - steps * self.m_x
        elif dir == "right":
            self.target[1] = self.target[1] + steps* self.m_y
        elif dir == "up":
            self.target[0] = self.target[0] - steps* self.m_x
        elif dir == "down":
            self.target[0] = self.target[0] + steps * self.m_y

        SetTask(self.redis_client, self.redis_keys, self.r_o, self.target)

    def updateQTable(self, s , a, sp, immediate_reward):

        ap = np.argmax(self.Q_TABLE[sp])
        self.Q_TABLE[s][a] = self.Q_TABLE[s][a] + self.lr*(immediate_reward + self.discount* self.Q_TABLE[sp][ap] - self.Q_TABLE[s][a])


    def save(self, save_path):
        np.savetxt(save_path, self.Q_TABLE, delimiter=',')

    def load(self, weights_path): 
        self.Q_TABLE = np.genfromtxt(weights_path, delimiter=',')

    def getMode(self):
        return self.mode
    
    def eval_mode(self, fast_eval = False):
        self.mode = "EVAL"
        if fast_eval:
            self.mode = "FAST_EVAL"

    def train_mode(self):
        self.mode = "TRAIN"

    def pickAction(self):
        pass

    def performAction(self):
        pass

    def train(self):
        pass

    def eval(self):
        pass

    def getState(self):
        pass

    def reset(self):
        self.path_index = 0
        self.target = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)



# #This is a simple q learning model to just move the base optimaly around the map
# class MazeModelContinuous(BaseMazeModel):

#     def __init__(self, redis_client , redis_keys, learning_params, robot_origin, goal_pos, maze_scale, num_states = 120, num_actions = 17,  weights = None):
#         super().__init__(redis_client, redis_keys, learning_params, robot_origin, goal_pos, maze_scale, num_states, num_actions,  weights)

#     def getObjectiveLoss(self, show_summary = False):

#         base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)
#         ee_pos = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)[:2]

#         r_min = 0.4 #HYPER PARAMETERS
#         r_max = 0.7 #HYPER PARAMETERS
#         optimal_R = 0.55 #HYPER PARAMETERS - has to match optimal r in discrete state
#         opt_thresh = 0.2 #HYPER PARAMETERS

#         base_radius = np.linalg.norm(base_pos)

#         radius_err = 0

#         if base_radius > r_max:
#             radius_err = -15*abs(base_radius - optimal_R)
#         elif base_radius < r_min:
#             radius_err = -15*abs(base_radius - optimal_R)
#         else:
#             radius_err = -1*abs(base_radius - optimal_R)

#         ideal_pos = optimal_R*(base_pos/np.linalg.norm(base_pos))

#         if np.linalg.norm(ee_pos) > 1e-2:
#             ideal_pos = optimal_R*(ee_pos/np.linalg.norm(ee_pos))

#         opt_d = np.linalg.norm(base_pos - ideal_pos)

#         opt_err = 0

#         if opt_d > opt_thresh:
#             opt_err = -20*opt_d
#         else:
#             opt_err = -1*opt_d


#         bed = np.linalg.norm(base_pos - ee_pos)
#         bed_err = 0

#         if bed > 0.3:
#             bed_err = -12*abs(bed - 0.3)
        
#         score = bed_err + opt_err + radius_err

#         if show_summary:
#             print("Summary: bed: {},  bed_err: {}".format(bed, bed_err))
#             print("Summary: opt_d: {}, opt_err: {}".format(opt_d, opt_err))
#             print("Summary: base_radius : {}, radius_err: {}".format(base_radius, radius_err))
#             print("Summary: total score: {}".format(score))

#         return score
    
#     def getState(self):
#         base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)
#         ee_pos = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)[:2]

#         r1 = 0.4 #Hyper Parameters
#         r2 = 0.5
#         r3 = 0.6
#         r4 = 0.7
#         optimal_R = 0.55
#         d_opt = 0.2
#         r = 0

#         if np.linalg.norm(base_pos) > r4:
#             r = 4
#         elif np.linalg.norm(base_pos) > r3:
#             r = 3
#         elif np.linalg.norm(base_pos) > r2:
#             r = 2
#         elif np.linalg.norm(base_pos) > r1:
#             r = 1
#         else:
#             r = 0

#         yp = -1*base_pos
#         rm = np.array([[0,1], [-1,0]])
#         xp = rm@yp

#         trans = np.column_stack([xp, yp])

#         optimal_pos = optimal_R*(base_pos/np.linalg.norm(base_pos))

#         if np.linalg.norm(ee_pos) > 1e-2:
#             optimal_pos = optimal_R*(ee_pos/np.linalg.norm(ee_pos))

#         optimal_pos_prime = np.linalg.solve(trans, optimal_pos)
#         opt_side = 0

#         if optimal_pos_prime[0] > 0:
#             opt_side = 1

#         opt_dist = 1

#         if np.linalg.norm(optimal_pos - base_pos) < d_opt:
#             opt_dist = 0

#         combo_list = [5, 2, 2]
#         indicators = [r, opt_dist, opt_side]
#         chunk = self.num_states
#         state_num = 0

#         for i in range(len(combo_list)):
#             chunk /= combo_list[i]
#             state_num += chunk*indicators[i]

#         return int(state_num)

#     def pickAction(self, greedy = False):

#         state = self.getState()
#         valid_actions = [i for i in  range(0,self.num_actions)]

#         best_action = random.choice(valid_actions)
        
#         if greedy:
#             best_action = int(np.argmax(self.Q_TABLE[state][valid_actions]))
#             best_action = valid_actions[best_action]
        
#         return best_action
    
#     def performAction(self, action):

#         speed = 0
#         direction = 0

#         if action != 0:
#             action -= 1

#             speed = action//8 + 1
#             action = action %8
#             direction = action

#         base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)

#         if speed == 0:
#             return base_pos
        
#         distance = 0.4 #HYPER PARAMETERS
#         otg_vel = 6 #HYPER PARAMETERS
#         otg_acc = 0.6 #HYPER PARAMETERS

#         if speed == 1:
#             distance = distance/2
#             otg_vel /= 2
#             otg_acc /= 2

#         theta = direction*math.pi/4

#         r = np.array([[math.cos(theta), -1*math.sin(theta)],[math.sin(theta), math.cos(theta)]])

#         cardinal_dir = base_pos.copy()/np.linalg.norm(base_pos)
#         cardinal_dir = r @ cardinal_dir
#         cardinal_dir = distance *cardinal_dir

#         target_pos = base_pos + cardinal_dir

#         SetMobileBaseVel(self.redis_client, self.redis_keys,np.array([otg_vel]))
#         SetMobileBaseAcc(self.redis_client, self.redis_keys,np.array([otg_acc]))
#         SetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o, target_pos)
        
#         return target_pos

#     def train(self, optimalPath, explore_rates, limit= None, eval_mode = False):
#         self.reset()
#         base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)

#         set_path = False
#         set_base = False

#         base_iter = 0
#         target_iter = 0
#         episode_iters = 0
#         average_error = 0

#         state_changes = 0
#         total_actions = 0

#         a = 0
#         s = -1
#         old_loss = -1

#         eps = explore_rates[self.path_index]

#         rn = random.random()
#         greedy = False

#         if rn > eps:
#             greedy = True

#         if eval_mode:
#             greedy = True

#         while total_actions < self.episode_len and (np.linalg.norm(base_pos - self.GOAL_POS) > 1e-2 or self.path_index <len(optimalPath)):
#             time.sleep(1/self.learn_freq)

#             if set_path == False and self.path_index < len(optimalPath):
#                 self.SolveMaze(optimalPath)
#                 set_path = True
#             else:
#                 curr_pos = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)
#                 target_iter += 1
#                 if np.linalg.norm(curr_pos - self.target) < 1e-3 or target_iter > self.TARGET_ITER:
#                     set_path = False
#                     target_iter = 0
#                     self.path_index += 1
#                     if limit is not None and self.path_index == limit:
#                         break
                
#             if set_base == False:

#                 s = self.getState()
#                 old_loss = self.getObjectiveLoss(show_summary= True)
#                 a = self.pickAction(greedy)
#                 total_actions += 1
#                 self.performAction(a)

#                 set_base = True
#                 base_iter = 0

#             else:
#                 base_iter += 1
#                 if base_iter > self.BASE_ITER:
#                     sp = self.getState()

#                     new_loss = self.getObjectiveLoss()
#                     immediate_reward = new_loss - old_loss 

                    
#                     self.updateQTable(s, a, sp, immediate_reward, eval_mode)

#                     set_base = False
#                     base_iter = 0

#             base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)
#             episode_iters += 1

#         print("Episode Iterations: {}".format(episode_iters))
#         print("State Change stats: {}".format(state_changes/total_actions))
#         return average_error/(self.path_index)
    
#     def eval(self, optimalPath, limit = None):
#         if self.mode != "EVAL" and self.mode != "FAST_EVAL":
#             raise Exception("model not in eval mode")
        
#         explore_rates = [1 for _ in range(len(optimalPath))]
#         self.train(optimalPath, explore_rates, limit, eval_mode=True)

class MazeModelSimple(BaseMazeModel):

    def __init__(self, redis_client , redis_keys, learning_params, robot_origin, goal_pos, maze_scale, num_states = 144, num_actions = 3,  weights = None):
        super().__init__(redis_client, redis_keys, learning_params, robot_origin, goal_pos, maze_scale, num_states, num_actions,  weights)
        self.num_zones = 12
        self.d_increment = 0.1
        self.num_distances = 6
        self.optimal_r = 0.55 #Hyper Parameters

        self.vel = 2
        self.acc = 0.2

        self.BASE_ITER = 200
        self.episode_len = 200
        self.TOTAL_ITER = 5000

        self.a_increment = 0.2


    def pickAction(self, greedy = False):

        state = self.getState()
        valid_actions = [i for i in range(0,self.num_actions)]

        best_action = random.choice(valid_actions)
        
        if greedy:
            best_action = int(np.argmax(self.Q_TABLE[state][valid_actions]))
            best_action = valid_actions[best_action]
        
        return best_action

    #Let us define action 1 to be anticlockwise and action 2 to be clockwise 
    def performAction(self, action):
        base_angle = GetBaseAngle(self.redis_client, self.redis_keys, self.r_o)

        if action == 0:
            return 0, 0

        #Perform action will be a whole different beast
        increment = (2 * math.pi)/self.num_zones

        direction = 0
        zone = math.floor(base_angle/increment)

        if action == 1:
            direction = -1
            zone -= 1
        elif action == 2:
            direction = 1
            zone += 1

        zone = zone%self.num_zones
            
        target_angle = zone * increment + increment/2
        target_position = np.array([self.optimal_r * math.cos(target_angle), self.optimal_r * math.sin(target_angle)])

        return target_position, direction
    

    def train(self, optimalPath, eps, limit = None, eval_mode = False):
        self.reset()

        if limit is None:
            limit = len(optimalPath)

        if self.mode != "TRAIN":
            raise Exception("model is not in train mode!")
        
        base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)

        task_state = "move_end_eff"
        base_state = "start_action"

        target_base_pos = np.array([0,0])

        target_iter = 0
        sub_base_iter = 0
        episode_iters = 0
        total_actions = 0

        total_reward = 0

        reached_target = False
        a = 0
        s = -1

        while total_actions < self.episode_len and not reached_target and episode_iters < self.TOTAL_ITER:
            time.sleep(1/self.learn_freq)
            base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)

            if task_state == "move_end_eff" and self.path_index < limit:
                self.SolveMaze(optimalPath)
                task_state = "in_movement"
            elif task_state == "in_movement":
                task_pos = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)
                target_iter += 1
                if np.linalg.norm(task_pos - self.target) < 1e-3 or target_iter > self.TARGET_ITER:
                    task_state = "move_end_eff"
                    target_iter = 0
                    self.path_index += 1
                
            if base_state == "start_action":
                rn = random.random()
                greedy = False

                if rn > eps:
                    greedy = True

                s = self.getState()
                a = self.pickAction(greedy)
                print("Picked action {}".format(a))
                total_actions += 1
                final_target, dir = self.performAction(a)
                base_state = "start_submovement"

            elif base_state == "start_submovement":
                if np.linalg.norm(final_target - base_pos) < 0.1 or a == 0:
                    print("completed_action")
                    base_state = "completed_action"
                    continue
                target_base_pos = InchBase(self.redis_client, self.redis_keys, self.r_o, self.optimal_r, self.a_increment, dir)
                base_state = "in_submovement"
                sub_base_iter = 0

            elif base_state == "in_submovement":
                sub_base_iter += 1

                if np.linalg.norm(base_pos - target_base_pos) < 1e-2 or sub_base_iter > 100:
                    base_state = "start_submovement"

            elif base_state == "completed_action":
                sp = self.getState()

                immediate_reward = self.calc_reward()

                if self.path_index == limit:
                    reached_target = True
                    
                total_reward += immediate_reward

                self.updateQTable(s, a, sp, immediate_reward)
                base_state = "start_action"

            base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)
            episode_iters += 1

        print("Total Reward: {}".format(total_reward))
        print("Episode Iters: {}".format(episode_iters))
        return -1

    def eval(self, optimalPath, limit = None):
        if self.mode != "EVAL" and self.mode != "FAST_EVAL":
            raise Exception("model not in eval mode")
        
        eps = 0
        self.mode = "TRAIN"
        self.train(optimalPath, eps, limit, eval_mode=True)
        self.mode = "FAST_EVAL"

    def getState(self, bp = None, eep = None, ba = None, show_summary = False):

        base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)
        ee_pos = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)[:2]
        base_angle = GetBaseAngle(self.redis_client, self.redis_keys, self.r_o)

        if bp is not None: 
            base_pos = bp
        
        if eep is not None:
            ee_pos = eep

        if ba is not None:
            base_angle = ba

        increment = (2 * math.pi)/self.num_zones
        zone = int(math.floor(base_angle/increment))
        ideal_pos = self.optimal_r*(base_pos/np.linalg.norm(base_pos))

        if np.linalg.norm(ee_pos) > 1e-2:
            ideal_pos = self.optimal_r*(ee_pos/np.linalg.norm(ee_pos))

        dist = np.linalg.norm(base_pos - ee_pos)
        dist_num = int(math.floor(dist/self.d_increment))

        if dist_num > self.num_distances -1:
            dist_num = 5

        yp = -1*base_pos
        rm = np.array([[0,1], [-1,0]])
        xp = rm@yp

        trans = np.column_stack([xp, yp])
        optimal_pos_prime = np.linalg.solve(trans, ideal_pos)
        ideal_side = 0

        if optimal_pos_prime[0] > 0:
            ideal_side = 1

        indicators = [zone, dist_num, ideal_side]

        if show_summary:
            print("indicators: {}".format(indicators))
            print("Actual stats: distance from ideal: {}".format(dist))

        state_num = self.toStateNum(indicators)

        return state_num
    
    def toStateNum(self, indicators):

        combo_list = [self.num_zones, self.num_distances, 2]

        chunk = self.num_states
        state_num = 0

        for i in range(len(combo_list)):
            chunk /= combo_list[i]
            state_num += chunk*indicators[i]

        return int(state_num)

    
    def calc_reward(self):

        base_pos = GetMobileBasePosition(self.redis_client, self.redis_keys, self.r_o)
        ee_pos = GetCartesianPosition(self.redis_client, self.redis_keys, self.r_o)[:2]

        ideal_pos = self.optimal_r*(base_pos/np.linalg.norm(base_pos))

        if np.linalg.norm(ee_pos) > 1e-2:
            ideal_pos = self.optimal_r*(ee_pos/np.linalg.norm(ee_pos))

        dist = np.linalg.norm(ideal_pos - base_pos)

        if dist > 0.3:
            return -10
        
        return -1




        


    

    






        

        
    



    

    
        



