# Data logging in Opensai

Some quantities are predetermined to be logged at will with Opensai on the controllers and simviz. The logging can be parametrized in the config file, and can be turned on and off at runtime via the proper redis key, or using the button in the webui interface. Be warned that if the timestamp is not included in the file name, stopping and restarting the logger for a robot controllers or the simviz will erase the previouw log file. The data is logged as a csv file. The header shows the logged quantities. When the logged data is a vector, the header will have the form `vector_name__i` where i is the ith coefficient of the vector. When it is a matrix, it will be logged as a vector of the successive rows of the matrix.

All the log files will be in the folder defined in the config file (by default called log_files/controllers and log_files/simviz).

## controllers data logging

A file called `<robot_name>_control.csv` will be created for each robot, that contains the following data:
- Time (since the logger started)
- Timestamp (os timestamp with format yyyy-mm-dd__hh-mm-ss.us)
- Joint positions
- Joint velocities
- Control torques
- Mass matrix

For each controller, a `<robot_name>_<controller_name>` folder will be created and contain a file per task.

The joint task will log the following info:
- Time (since the logger started)
- Timestamp (os timestamp with format yyyy-mm-dd__hh-mm-ss.us)
- Gains (kp, kv, ki)
- Velocity saturation parameters
- OTG parameters
- goal positions, velocities and accelerations
- current positions, velocities and accelerations
- desired positions, velocities and accelerations (correspond to the output of otg if enabled, equal to the goals of not)
- whether dynamic decoupling is enabled
- whether the controller this task belongs to is active

The motion force task will have the following info
- Time (since the logger started)
- Timestamp (os timestamp with format yyyy-mm-dd__hh-mm-ss.us)
- Gains (kp, kv, ki for position, orientation, force and moment)
- Force and moment space parametrization
- Velocity saturation parameters
- OTG parameters
- goal position, linear velocity and linear acceleration, orientation, angular velocity and angular acceleration
- current position, linear velocity and linear acceleration, orientation, angular velocity and angular acceleration
- linear position, linear velocity and linear acceleration, orientation, angular velocity and angular acceleration (correspond to the output of otg if enabled, equal to the goals of not)
- desired forces and moments
- sensed forces and moments
- whether dynamic decoupling is enabled
- whether the controller this task belongs to is active
- whether the force control is closed loop

## simviz data logging

For each object and robot, a file will be created called `<robot_or_object_name>_simviz.csv`.

The robot files contain the following information:
- Time (since the logger started)
- Timestamp (os timestamp with format yyyy-mm-dd__hh-mm-ss.us)
- Joint position and velocities
- Control torques
- Ui torques (torques applied by right clicking on the robot)
- Sensed forces and moments for all sensors attached to the robot

The object files contain the following information:
- Time (since the logger started)
- Timestamp (os timestamp with format yyyy-mm-dd__hh-mm-ss.us)
- Pose and velocities
- Ui torques (torques applied by right clicking on the object)
- Sensed forces and moments for all sensors attached to the object

## visualizing data

There are 2 ways of visualizing data in Opensai. The online plotter (available by clicking the corresponding button in the webui) can plot redis data in real time, with a limited rate. To visualize the csv files recorede by the logger, a simple utility program is provided. It can be opened by clicking the `Open offline CSV plotter` button in the webui, or directly by opening the python program with the following command from the Opensai root folder `python3 bin/ui/csv_plotter.py`. In the window that opens, you can load a csv file and select the quantities to plot, select a totle for the plot, and plot it in a browser using plotly.
