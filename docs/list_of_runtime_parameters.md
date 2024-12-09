# List of interactive config parameters for SAI simviz and controllers

A lot of the controllers and simviz parameters defined in the configuration file can be changed at runtime via redis. We will list and describe all of them here.

## Controllers

For a given robot that has controllers attached to it, there are several robot level parameters that can be set to start/stop the data logging or switch controllers for example. For a given robot, the control parameters redis keys will be prefixed by `<namespace_prefix>::controllers::<robot_name>::`.

| parameter | description | type | example key |
| ------ | ------ | ------ | ------ |
| active_controller_name | the name of the active controller for that robot. Can be changed to switch to another controller that was defined in the config file for that robot | a string | sai::controllers::Panda::active_controller_name |
| logging_on | set to 1 to start logging data for that robot (will log data for all the controllers) and to 0 to stop logging data | a boolean represented by "1" or "0" | sai::controllers::Panda::logging_on |

In addition, there are a lot of parameters that can be set for the different controller tasks. The corresponding redis keys are prefixed by `<namespace_prefix>::controllers::<robot_name>::<controller_name>::<task_name>::<parameter>`.

### Joint tasks parameters

| parameter | description | type | example key |
| ------- | ------- | ------- | ------- |
| kp | P gains for the task PID controller | a scalar or a vector of size 1 or a vector of the same size as the task dofs | sai::controllers::Panda::joint_controller::<br>joint_task::kp |
| kv | D gains for the task PID controller | a scalar or a vector of size 1 or a vector of the same size as the task dofs | sai::controllers::Panda::joint_controller::<br>joint_task::kv |
| ki | I gains for the task PID controller | a scalar or a vector of size 1 or a vector of the same size as the task dofs | sai::controllers::Panda::joint_controller::<br>joint_task::ki |
| use_dynamic_decoupling | whether to use dynamic decoupling for the task or not | a boolean represented by "1" or "0" | sai::controllers::Panda::joint_controller::<br>joint_task::use_dynamic_decoupling |
| velocity_saturation_enabled | whether to use velocity saturation for the task | a boolean represented by "1" or "0" | sai::controllers::Panda::joint_controller::<br>joint_task::velocity_saturation_enabled |
| velocity_saturation_limit | the values of the max velocity for the velocity saturation | a scalar or a vector of size 1 or a vector of the same size as the task dofs | sai::controllers::Panda::joint_controller::<br>joint_task::velocity_saturation_limit |
| otg_enabled | whether to enable the task internal online trajectory generation | a boolean represented by "1" or "0" | sai::controllers::Panda::joint_controller::<br>joint_task::otg_enabled |
| otg_jerk_limited | whether to use acceleration limited or jerk limited online trajectory generation | a boolean represented by "1" or "0" | sai::controllers::Panda::joint_controller::<br>joint_task::otg_jerk_limited |
| otg_max_velocity | the maximum velocity for the online trajectory generation | a scalar or a vector of size 1 or a vector of the same size as the task dofs | sai::controllers::Panda::joint_controller::<br>joint_task::otg_max_velocity |
| otg_max_acceleration | the maximum acceleration for the online trajectory generation | a scalar or a vector of size 1 or a vector of the same size as the task dofs | sai::controllers::Panda::joint_controller::<br>joint_task::otg_max_acceleration |
| otg_max_jerk | the maximum jerk for the online trajectory generation (only used if jerk limited otg is enabled) | a scalar or a vector of size 1 or a vector of the same size as the task dofs | sai::controllers::Panda::joint_controller::<br>joint_task::otg_max_jerk |

### Motion force task parameters

| parameter | description | type | example key |
| ------- | ------- | ------- | ------- |
| use_dynamic_decoupling | whether to use dynamic decoupling for the task or not | a boolean represented by "1" or "0" | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::use_dynamic_decoupling |
| position_kp | the P gain for the translation part of the motion controller | a scalar or a vector of size 1 or a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::position_kp |
| position_kv | the D gain for the translation part of the motion controller | a scalar or a vector of size 1 or a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::position_kv |
| position_ki | the I gain for the translation part of the motion controller | a scalar or a vector of size 1 or a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::position_ki |
| orientation_kp | the P gain for the rotation part of the motion controller | a scalar or a vector of size 1 or a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::orientation_kp |
| orientation_kv | the D gain for the rotation part of the motion controller | a scalar or a vector of size 1 or a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::orientation_kv |
| orientation_ki | the I gain for the rotation part of the motion controller | a scalar or a vector of size 1 or a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::orientation_ki |
| closed_loop_force_control | whether the force controller is closed loop or open loop | a boolean represented by "0" or "1" |  sai::controllers::Panda::cartesian_controller::<br>cartesian_task::closed_loop_force_control |
| force_kp | the P gain for the translation part of the force controller | a scalar or a vector of size 1 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::force_kp |
| force_kv | the D gain for the translation part of the force controller | a scalar or a vector of size 1 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::force_kv |
| force_ki | the I gain for the translation part of the force controller | a scalar or a vector of size 1 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::force_ki |
| moment_kp | the P gain for the translation part of the moment controller | a scalar or a vector of size 1 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::moment_kp |
| moment_kv | the D gain for the translation part of the moment controller | a scalar or a vector of size 1 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::moment_kv |
| moment_ki | the I gain for the translation part of the moment controller | a scalar or a vector of size 1 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::moment_ki |
| force_space_dimension | the dimension of the force space (0 to 3, 0 for full motion control, 3 for full force control) | an int | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::force_space_dimension |
| moment_space_dimension | the dimension of the moment space (0 to 3, 0 for full motion control, 3 for full moment control) | an int | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::moment_space_dimension |
| force_space_axis | the axis of the 1 dof space (force if force space dimention is 1, motion if force space dimension is 2) in translation | a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::force_space_axis |
| moment_space_axis | the axis of the 1 dof space (moment if moment space dimention is 1, motion if moment space dimension is 2) in rotation | a vector of size 3 | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::moment_space_axis |
| velocity_saturation_enabled | whether the velocity saturation is enabled | a boolean represented by "0" or "1" | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::velocity_saturation_enabled |
| linear_velocity_saturation_limit | max linear velocity for the velocity saturation | a scalar | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::linear_velocity_saturation_limit |
| angular_velocity_saturation_limit | max angular velocity for the velocity saturation | a scalar | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::angular_velocity_saturation_limit |
| otg_enabled | whether the internal online trajectory generation is enabled | a boolean represented by "0" or "1" | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_enabled |
| otg_jerk_limited | whether the internal online trajectory generation implements jerk limits or not | a boolean represented by "0" or "1" | sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_jerk_limited |
| otg_max_linear_velocity | the linear velocity limit for the internal OTG | a scalar |sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_max_linear_velocity |
| otg_max_angular_velocity | the angular velocity limit for the internal OTG | a scalar |sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_max_angular_velocity |
| otg_max_linear_acceleration | the linear acceleration limit for the internal OTG | a scalar |sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_max_linear_acceleration |
| otg_max_angular_acceleration | the angular acceleration limit for the internal OTG | a scalar |sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_max_angular_acceleration |
| otg_max_linear_jerk | the linear jerk limit for the internal OTG if jerk_limited_otg is enabled | a scalar |sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_max_linear_jerk |
| otg_max_angular_jerk | the angular jerk limit for the internal OTG if jerk_limited_otg is enabled | a scalar |sai::controllers::Panda::cartesian_controller::<br>cartesian_task::otg_max_angular_jerk |
