# OpenSai

## Install Instructions

Start by installing the dependencies:

```
sh scripts/install_dependencies.sh
```

Then call the setup script that will create a core folder and download and compile all the core sai2 libraries there. It will also install all the python requirements for the interface.

```
sh scripts/install_core_libraries.sh
```

Finally, build the OpenSai_main application (which will be located in the bin folder)

```
sh scripts/build_Opensai.sh
```

## Usage Instructions

You can start OpenSai main application with a given config file in 4 steps:
1. Start the redis server (if not already running). In a new terminal, type `redis-server`
2. Start the OpenSai main application and provide a config file as argument. The config files must be in the `config_folder/xml_config_files` folder. If no config file name is provided, it will use the `single_panda.xml` file by default

```
./bin/OpenSai_main <optional-config-file-name>
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

## Interacting with the controller using Redis and Python

It is possible to interact with the controllers and simulation directly via Redis, without going through the webui. The redis values are string, and use json representation for vectors/arrays and complex data structures.
The redis keys are decomposed in namespaces. The default namespace prefix is `sai2::interfaces::` if not specified in the config file. In all Opensai examples, the prefix will be `opensai::`. The redis keys are then constructed using the names of the robots or objects, the controller names, task names and finally the specific key. For example, the key to change the gains of the task named `joint_task` in the controller named `cartesian_controller` for the robot `Panda` will be `opensai::controller::Panda::cartesian_controller::joint_task::kp`. You can open a redis client in terminal to look at the redis keys and get their value to print using the `get` command in order to examine them. You can also set a key with the `set` command. After running the main example, open a new terminal and:
```
redis-cli
127.0.0.1:6379> keys *
 1) "opensai::controllers::Panda::joint_controller::joint_task::gains_safety_checks_enabled"
 2) "opensai::controllers::Panda::cartesian_controller::joint_task::otg_max_acceleration"
 3) "opensai::controllers::Panda::cartesian_controller::joint_task::otg_max_velocity"
 4) "opensai::controllers::Panda::joint_controller::joint_task::kp"
 ...
 127.0.0.1:6379> get opensai::sensors::Panda::joint_positions
"[0.000000,-0.436332,-0.000000,-2.356195,0.000000,1.832597,-0.000000]"
```
See the documentation section for the links to a complete description of all the redis keys published or listened to by the controllers.

In particular, it is very easy to use python scripts to create state machine and interact with the controllers using redis. The python_examples folder contains some examples. You can try the `panda_left_right.py` example that will move the robot end effector from left to right. first, launch the Opensai main program with the default config
```
sh scripts/launch.sh
```

and then, in another terminal, you can start the python script
```
python3 python_examples/panda_left_right.py
```

For a detailled list of all the inputs, parameters and outputs of the controller and simulation, see the documentation below.

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
Opensai offers the possibility to log data from the controllers and simulation. The data logged is pre determined from the different robots and tasks in the controllers, and from the robots and objects in the world for the simulation. The logging files location, logging frequency and other options can be set in the config file, and the logging can be turned on and off via a redis message.

See [here](docs/data_logging.md) for a list of all the logged data

## Documentation

OpenSai main application is an instance of the MainRedisInterface application from the [sai2-interfaces](https://github.com/manips-sai-org/sai2-interfaces) library. You can interact with the controller and simulation from the webui on the browser. For an overview of the ui and how to use it, see [this page](https://github.com/manips-sai-org/sai2-interfaces/blob/master/docs/ui_overview.md). For details on the config files, how to use them and how to make your own for your application, see [here](https://github.com/manips-sai-org/sai2-interfaces/blob/master/docs/config_files_details.md).

The following pages list all the redis keys generated by the main Opensai program and what they correspond to.
- [List of inputs and outputs](docs/list_of_inputs_outputs.md) (sensor values, task goals, commands and monitoring outputs)
- [List of interactive config parameters](docs/list_of_runtime_parameters.md) (to change the parametrization at runtime)

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
