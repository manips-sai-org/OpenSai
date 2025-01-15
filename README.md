# SAI

SAI (for Simulation and Active Interfaces) is a Software Framework for robot simulation and control. It provides a simulator, graphics visualizer, control library and interfaces to interact with those. The control library is aimed at controlling torque controlled robots, so the output of the controller is a vector of command joint torques.

The different part of the framework communicate between each other using redis as a middleware.

## Install Instructions

Start by installing the dependencies:

```
sh scripts/install_dependencies.sh
```

Then call the setup script that will create a core folder and download and compile all the core sai libraries there. It will also install all the python requirements for the interface.

```
sh scripts/install_core_libraries.sh
```

Finally, build the SAI_main application (which will be located in the bin folder)

```
sh scripts/build_SAI_main.sh
```


## Tutorials
We provide tutorials to guide new users towards most of the basic functions.
- The [first tutorial](tutorials/docs/1_pendulum.md) focuses on the simulation and graphics options, how to make a robot model, world file and config file, and how to use the UI.
- The [second tutorial](tutorials/docs/2_panda.md) focuses on the controllers. How to control a robot arm, and what are the different options and ways of interacting with the controller
- The [third tutorial](tutorials/docs/3_panda_haptic.md) shows how to add a haptic controller to control a robot end effector

We also provide other pre built examples and some documentation (see below).

## Usage Instructions

You can start SAI main application with a given config file in 4 steps:
1. Start the redis server (if not already running). In a new terminal, type `redis-server`
2. Start the SAI main application and provide a config file as argument. The config files must be in the `config_folder/xml_config_files` folder. If no config file name is provided, it will use the `single_panda.xml` file by default

```
./bin/SAI_main <optional-config-file-name>
```

3. Start the webui server with the generated file from the main application

```
python3 bin/ui/server.py config_folder/xml_config_files/webui_generated_file/webui.html
```

4. Open a web browser and navigate to `localhost:8000`

Alternatively, we provide a script that performs the first 3 steps automatically and you can provide the config file name as argument

```
sh scripts/launch.sh <optional-config-file-name>
```

If using the script, you will still need to manually open a web browser and navigate to `localhost:8000` in order to use the webui.

From the UI, you can load any config file from the `config_folder/xml_config_files` folder and interact with the robot controllers. Files in other folders will not work.
You can make new applications by making new config files and placing them in the `config_folder/xml_config_files` folder.

### Using real hardware instead of simulated robots
When using real hardware, make sure to use a config file that does not launch a simulation (either put the simviz in vizOnly mode, or don't have a simviz configuration at all in the config file). The controllers can interact with any robot that provides the required inputs via redis (joint angles, joint velocities, and mass matrix if possible), and reads the command torques via redis. Make sure your robot program uses the same redis keys as the SAI controller.

__IMPORTANT__: Make sure to know if your robot driver performs gravity compensation, and if it publishes the mass matrix to redis, and configure your controller in function:
- If you want a controller to perform gravity compensation, set the attribute `gravityCompensation="true"` in the corresponding `<controller>` tag. The value is false by default if omitted because the robots drivers we use with SAI perform gravity compensation already.
- If you want your controller to compute the mass matrix from the urdf file instead of getting it from the robot driver, Make sure to set the `getMassMatrixFromRedis` attribute to `false` in the config file (`robotControlConfiguration` tag). It is false by default if omitted because the robot drivers we use with SAI publish it, and the urdf models don't have a good estimate of the inertial parameters.

For convenience, we provide redis drivers for the following hardware, that should be useable immediatly with SAI controllers:
- Franka robots (FR3 and Panda): [FrankaPanda repository](https://github.com/manips-sai/FrankaPanda)
- Flexiv robots (Internal API not provided, Rizon4 and Rizon4s supported): [FlexivRizonRedisDriver repository](https://github.com/manips-sai-org/FlexivRizonRedisDriver)
- ATI Gamma 6 axis Force/Torque sensor: [ATIGamma_redis_driver repository](https://github.com/manips-sai-org/ATIGamma_redis_driver)
- Haptic devices compatible with chai3d (all ForceDimension devices and many more): [chaiHapticDeviceRedisDriver repository](https://github.com/manips-sai-org/chaiHapticdeviceRedisDriver)

## Interacting with the controller using Redis and Python

It is possible to interact with the controllers and simulation directly via Redis, without going through the webui. The redis values are string, and use json representation for vectors/arrays and complex data structures.
The redis keys are decomposed in namespaces. The default namespace prefix is `sai::interfaces::` if not specified in the config file. In all SAI examples, the prefix will be `sai::`. The redis keys are then constructed using the names of the robots or objects, the controller names, task names and finally the specific key. For example, the key to change the gains of the task named `joint_task` in the controller named `cartesian_controller` for the robot `Panda` will be `sai::controller::Panda::cartesian_controller::joint_task::kp`. You can open a redis client in terminal to look at the redis keys and get their value to print using the `get` command in order to examine them. You can also set a key with the `set` command. After running the main example, open a new terminal and:
```
redis-cli
127.0.0.1:6379> keys *
 1) "sai::controllers::Panda::joint_controller::joint_task::gains_safety_checks_enabled"
 2) "sai::controllers::Panda::cartesian_controller::joint_task::otg_max_acceleration"
 3) "sai::controllers::Panda::cartesian_controller::joint_task::otg_max_velocity"
 4) "sai::controllers::Panda::joint_controller::joint_task::kp"
 ...
 127.0.0.1:6379> get sai::sensors::Panda::joint_positions
"[0.000000,-0.436332,-0.000000,-2.356195,0.000000,1.832597,-0.000000]"
```
See the documentation section for the links to a complete description of all the redis keys published or listened to by the controllers.

In particular, it is very easy to use python scripts to create state machine and interact with the controllers using redis. The python_examples folder contains some examples. You can try the `panda_left_right.py` example that will move the robot end effector from left to right. first, launch the SAI main program with the default config
```
sh scripts/launch.sh
```

and then, in another terminal, you can start the python script
```
python3 python_examples/panda_left_right.py
```

For a detailled list of all the inputs, parameters and outputs of the controller and simulation, see the documentation below.

## List of examples
We provide several examples in the `config_folder/xml_config_files` folder. To run one of those exammples, you can run
```
sh scripts/launch.sh <config_file_name>.xml
```

You can also provide the full absolute or relatove path to the config file you want to use.

Some of these examples also provide an associated python script example to perform certain actions. Here is the list of the examples with a quick description:

- `single_panda.xml`. It is the default example. It simulates a panda arm on a floor with a box dynamic object. The panda has a cartesian controller with two tasks (6dof motion force task and joint task in the nullspace) and a joint controller. You can use the python script `panda_left_right.py` to control the robot to move left and right successively.
- `single_panda_peg.xml`. The only difference is the end effector of the robot that was changed to a peg.
- `single_panda_gripper.xml`. The panda has the gripper attached. The controller had a gripper finger task which is a joint task to move the fingers of the grippers. You can use the python script `panda_gripper_pick_place.py` to start a state machine that will pick the orange cube and place it on the other table.
- `panda_allegro.xml`. The panda has an allegro hand attached. The cartesian controller has a partial joint task to control the finger joints and the motion force task controls the palm of the hand.
- `double_panda.xml`. Two panda next to each other are simulated and controlled.
- `kuka_object_friction.xml`. A kuka robot is simulated and controlled. It has a flat end effector, and the world has a table and yellow disk that can slide on the table. you can use the python script `kuka_move_object_with_friction.py` to start a state machine that will move the object by pressing on it against the table and move it towards the robot.
- `kuka_plate_table.xml`. A kuka robot and a table that can tilt in the x-y plane (implemented as a robot). You can use the python script `kuka_surface_alignemnt.py` to start a state machine that will pivot the table and control the kuka robot to perform surface-surface alignemnt.

## High level overview of the controllers
The controllers are defined as a sequence of task and are implemented as a hierarchical controller with dynamic decoupling between the different task levels. On each task, the controller can implement task level dynamic decoupling or not. When dynamic decoupling is enabled, the operational space inertia matrix is used in the control law to control the task as a unit mass system, if it is disabled, the task space mass matrix is not used at the task control level, and the task controller is aparented to an impedance controller. The tasks support velocity saturation, which in essence saturates the task error (and therefore the task force) in order to limit the velocity. They also implement internal online trajectory generation on the task DoFs using the [Ruckig](https://ruckig.com) library for motion control. When internal otg is enabled, the goal position and velocity will be used as the input of ruckig, which outputs the desired position used in the PID controller. When internal otg is off, the input of the PID controller is directly the goal position, velocity and acceleration.

For motion force tasks, we can parametrize the motion and force space (in both translation and rotation) by defining the force space dimension (0 to 3) and one axis that will represent the force axis if the force space dimension is 1, and the motion axis if the force space dimension is 2. See the surface surface alignment script for an example usage.

For beginner users, it is recommended to enable OTG and disable velocity saturation (which is the default behavior).

Here is a summary of the inputs and parameters that the tasks can accept (for details, look at the documentation section)
- Goals positions, velocities, accelerations
- Desired forces and moments
- Force space parametrization
- Enabling or disabling dynamic decoupling between the tasks directions.
- Gains
- Velocity saturation parameters
- Internal OTG parameters

## Data logging
SAI offers the possibility to log data from the controllers and simulation. The data logged is pre determined from the different robots and tasks in the controllers, and from the robots and objects in the world for the simulation. The logging files location, logging frequency and other options can be set in the config file, and the logging can be turned on and off via a redis message.

See [here](docs/data_logging.md) for a list of all the logged data

## Documentation
SAI main application is an instance of the MainRedisInterface application from the [sai-interfaces](https://github.com/manips-sai-org/sai-interfaces) library. You can interact with the controller and simulation from the webui on the browser. For an overview of the ui and how to use it, see [this page](https://github.com/manips-sai-org/sai-interfaces/blob/master/docs/ui_overview.md). For details on the config files, how to use them and how to make your own for your application, see [here](https://github.com/manips-sai-org/sai-interfaces/blob/master/docs/config_files_details.md).

The following pages list all the redis keys generated by the main SAI program and what they correspond to.
- [List of inputs and outputs](docs/list_of_inputs_outputs.md) (sensor values, task goals, commands and monitoring outputs)
- [List of interactive config parameters](docs/list_of_runtime_parameters.md) (to change the parametrization at runtime)

## Note on supported graphics files
SAI uses [chai3d](https://www.chai3d.org) under the hood for graphics rendering. The rendering supports visuals defined by primitive shapes (box, shpere, cylinder) and the following mesh file formats:
- obj (with associated mtl files)
- 3ds
- stl (binary stl only, not ascii stl)
Files using other format can be converted using a software like [blender](https://www.blender.org).

#### Notes on converting files to obj with blender 
* When converting files to obj using blender, the associated mtl will often have a line defining the Ka value that will put all the Ka values to 1: `Ka 1.000000 1.000000 1.000000`. This will make all the material appear white as they will emit white light. You will need to replace this with `Ka 0.000000 0.000000 0.000000` in order to see the actual colors of the material definition.
* When converting files using blender, be careful to keep the same import and export conditions (for example, Y forward, Z up). Different file formats tend to have different default conventions.


## Updating the core libraries

To pull the latest updates from the core libraries, you can use the provided script that will checkout the master branch of all core libraries and pull the latest changes.

```
sh scripts/update_core_libraries.sh
```

Don't forget to re install them afterwards, and to re build the main application.

## Uninstall instructions

The core libraries are installed for the current OS session user, and the main application is not installed globally. The uninstall script will remove the build and cmake output for all core libraries and the main application:

```
sh scripts/uninstall.sh
```

## License
Currently pending licensing. PLEASE DO NOT DISTRIBUTE.