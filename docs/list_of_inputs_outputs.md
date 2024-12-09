# List of inputs and outputs for Opensai simviz and controllers

There are 2 types of controller inputs:
- Sensor data for the feedback control loops
- Task goals

There are 2 types of controller outputs:
- Robot commands
- Data for monitoring

For the simulation and visualizer, it depends on the mode.
- If the simviz runs in visualizer only mode, the inputs are robots and object positions
- If the simulation is enabled, the inputs are the robot commands, and the outputs are the sensor data on robots and objects

## Sensor data

As mentioned before, the sensor data is the input of the controllers, and it can come from the simulation or the different robot and sensor drivers if using a real world system.

### Controller input

The redis keys for the sensors are organized as follows `<namespace_prefix>::sensors::<robot_or_object_name>::<sensor_specific_suffix>`. The namespace_prefix is to be defined in the config file. It can be empty. The robot or object name is as defined in the world file if using the simulation. If using the actual robot, make sure the robot name in the control specification match the robot name provided by the driver. The following table lists the required sensor info for all robot controllers.

| sensor_specific_suffix | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| joint_positions | the position of the robot joints | a vector of the same size as the robot DoFs | opensai::sensors::Panda::joint_positions |
| joint_velocities | the velocities of the robot joint | a vector of the same size as the robot DoFs | opensai::sensors::Panda::joint_velocities |
| model::mass_matrix | the robot mass matrix (optionnal). Used as an input if the parameter readMassMatrixFromRedis is set to true in the config | a square matrix of the same size as the robot DoFs | opensai::sensors::Panda::model::mass_matrix |

The simulation and controllers also supports force torque sensors on the robots or objects. For those, the sensor specific information will contain the link name of the link where the sensor is attached. If the controller implements a motion force task on a link, it will expect force torque information on that robot on that link in order to implement closed loop force control. 

| sensor_specific_suffix | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| ft_sensor::<link_name>::force | the force that the sensor on that robot link applies to the environment, in the sensor frame | a vector of 3 values | opensai::sensors::Panda::ft_sensor::<br>end-effector::force |
| ft_sensor::<link_name>::moment | the moment that the sensor on that robot link applies to the environment, in the sensor frame | a vector of 3 values | opensai::sensors::Panda::ft_sensor::<br>end-effector::moment |

### Other sensor data provided by the simulation
The simulation also supports force sensors on objects, as well as object pose and velocity estimation. The information is not used directly used by the controller, but it can be used by the planner to provide tasks goals for example. On the force sensor, the link name is ommitted for objects.

| sensor_specific_suffix | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| ft_sensor::force | the force that the sensor on that object link applies to the environment, in the sensor frame | a vector of 3 values | opensai::sensors::Box::ft_sensor::force |
| ft_sensor::moment | the moment that the sensor on that object link applies to the environment, in the sensor frame | a vector of 3 values | opensai::sensors::Box::ft_sensor::moment |
| object_pose | the pose of the object in the world frame | a 4x4 transformation matrix | opensai::sensors::Box::object_pose |
| object_velocity | the velocity (linear first and angular second) of the object | a vector of 6 values (3 linear velocity and 3 angular velocity) | opensai::sensors::Box::object_velocity |

## Task goals

Each robot can have one or multiple controllers, each controller is composed of one or several tasks. The task goals for a given task can be set to redis using a redis key constructed as follows: `<namespace_prefix>::controllers::<robot_name>::<controller_name>::<task_name>::<task_goal>`.

The following are the task goals for joint tasks

| task_goal | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| goal_position | the goal position of the joints | a vector of the same size as the task DoFs  | opensai::controllers::Panda::joint_controller::<br>joint_task::goal_position |
| goal_velocity | the goal velocity of the joints | a vector of the same size as the task DoFs  | opensai::controllers::Panda::joint_controller::<br>joint_task::goal_velocity |
| goal_acceleration | the goal acceleration of the joints | a vector of the same size as the task DoFs  | opensai::controllers::Panda::joint_controller::<br>joint_task::goal_acceleration |

The following are the task goals for motion force task

| task_goal | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| goal_position | the cartesian task goal position | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::goal_position |
| goal_orientation | the cartesian task goal orientation | a 3d rotation matrix  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::goal_orientation |
| goal_linear_velocity | the cartesian task goal linear velocity | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::goal_linear_velocity |
| goal_angular_velocity | the cartesian task goal angular velocity | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::goal_angular_velocity |
| goal_linear_acceleration | the cartesian task goal linear acceleration | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::goal_linear_acceleration |
| goal_angular_acceleration | the cartesian task goal angular acceleration | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::goal_angular_acceleration |
| desired_force | the cartesian task desired force that the end effector should apply to the environment | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::desired_force |
| desired_moment | the cartesian task desired moment that the end effector should apply to the environment | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::desired_moment |

## Robot commands

The controller outputs robot command that are used by the simulation or the actual robot driver. The command redis key is constructed as follows : `<namespace_prefix>::commands::<robot_name>::<command_type>`

| command_type | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| control_torques | torques to be applied to the robot joints | a vector with the same size as the robot DoFs | opensai::commands::Panda::control_torques|

## Data for monitoring

In addition to storing all the data required by the robot controllers and simviz, some data is also published to redis by the controller only for monitoring purpose (it is not used by the simulation or robot drivers).

The monitoring data includes the list of joint names corresponding to the ordering used in all vectors (joint positions, velocities and command torques for that robot) as well as a boolean indicating if the controller is currently running or not for that robot.

| monitoring data | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| is_running | true if the controller for that robot is currently running, false otherwise | a boolean | opensai::controllers::Panda::is_running |
| joint_names | the list of joint names in the same order as the order used for q, dq and the torques | a list of names (str) | opensai::controllers::Panda::joint_names |

The rest of the monitoring data is controller and task specific so the redis key is contructed as follows : `<namespace_prefix>::controllers::<robot_name>::<controller_name>::<task_name>::<monitoring_data>`.

monitoring data for joint tasks

| monitoring data | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| current_position | the position of the joints involved in the joint task | a vector of the same size as the task DoFs | opensai::controllers::Panda::joint_controller::<br>joint_task::current_position |
| current_velocity | the velocity of the joints involved in the joint task | a vector of the same size as the task DoFs | opensai::controllers::Panda::joint_controller::<br>joint_task::current_velocity |

monitoring data for motion force tasks

| monitoring data | description | type | example of full key |
| -------- | ------- | ------- | -------- |
| current_position | the cartesian task current position | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::current_position |
| current_orientation | the cartesian task current orientation | a 3d rotation matrix  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::current_orientation |
| current_linear_velocity | the cartesian task current linear velocity | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::current_linear_velocity |
| current_angular_velocity | the cartesian task current angular velocity | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::current_angular_velocity |
| sensed_force | the cartesian task sensed force that the end effector should apply to the environment, resolved at the control frame | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::sensed_force |
| sensed_moment | the cartesian task sensed moment that the end effector should apply to the environment, resolved at the control frame | a 3d vector  | opensai::controllers::Panda::cartesian_controller::<br>cartesian_task::sensed_moment |

