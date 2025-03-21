# Tutorial 1 - Simulation with pendulums

This tutorial aims at showcasing the main features of OpenSai when defining a simulation world. All the tutorial files are present in the `tutorials` folder.

A very basic and uncomplete simulation is provided. Following this tutorial, you will learn how to complete the roboti model, add things to the simulation and interact with it.

## Launching the simulation and understanding the config files

First, launch the first tutorial. From the root folder of the OpenSai repository:

```
sh scripts/tutorial_launch.sh 1
```

You should see a window opening, showing a sphere and cylinder on a black background:
![](images/1_initial_simulation.png)

This represents a simple pendulum, hanging vertically, attached to the world on its upper sphere. there are already a few things that you can do with this simulation:
* move, zoom and unzoom the camera using the mouse (scrolling wheel, left click + drag, center click + drag, crtl + left click + drag, shift + left click + drag, arrow keys, A or Z keys)
* interact with the pendulum by right clicking on the cylinder sphere and dragging it left or right

Note that the gravity seems not to afect the pendulum. We will change this soon.

In order to define a simulation in OpenSai, we need 3 types of files. We need a xml config file for the OpenSai simulation definition, we need a world file to define the virtual world, and we need a urdf file for each robot we want to simulate (in the current case, for the pendulum). Let's look at those files.

* The urdf file for the pendulum is located in `tutorials/tuto_config_folder/robot_files/pendulum.urdf` and its contents are:

```
<?xml version="1.0" ?>

<robot name="pendulum">

	<link name="base_link">
		<inertial>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<mass value="1" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<geometry>
				<sphere radius="0.1" />
			</geometry>
		</visual>
	</link>
	<link name="link1">
		<inertial>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<mass value="1.0" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<geometry>
				<cylinder radius="0.07" length="1" />
			</geometry>
		</visual>
	</link>

	<joint name="j0" type="revolute">
		<parent link="base_link" />
		<child link="link1" />
		<origin xyz="0 0 0"/>
		<axis xyz="1 0 0" />
		<limit lower="-2.967" upper="2.967" effort="176" velocity="1.7104" />
	</joint>

</robot>
```

In order to define a robot model in the URDF format, we need to define links and joints. The kinematic structure of the robot is defined by the joints. Each joint has a type, a parent, a child, a position in its parent joint. For more information, look at the [ROS official URDF documentation](https://wiki.ros.org/urdf/XML/model)

The links are used to define inertial properties, visual and collision elements. Inertial properties are mandatory in OpenSai, visual and collision elements are optional.

* The world file is `tutorials/tuto_config_folder/world_files/1_pendulum_world.urdf`. Its content is

```
<?xml version="1.0" ?>

<world name="tuto_1_world" gravity="0.0 0.0 -9.81">

	<robot name="pendulum">
		<model dir="${TUTORIALS_ROBOT_FILES_FOLDER}" path="pendulum.urdf" name="pendulum" />
	</robot>

	<light name="light1" type="directional">
		<position xyz="2.0 -2.0 2.0" />
		<lookat xyz="0.0 0.0 0.0" />
	</light>

	<light name="light2" type="directional">
		<position xyz="2.0 2.0 2.0" />
		<lookat xyz="0.0 0.0 0.0" />
	</light>

	<camera name="camera_fixed">
		<position xyz="3.0 0.0 0.0" />
		<vertical xyz="0.0 0.0 1.0" />
		<lookat xyz="0.0 0.0 -0.5" />
	</camera>

</world>
```

The world file contains robot models, objects (there are no objects presents in this example yet), lights and cameras to render the world. Note that it also defined the world gravity. we will see a little later why it does not affect the pendulum.

* The OpenSai configuration file is `tutorials/tuto_config_folder/xml_files/1_pendulum.xml`. For now, it is very simple:

```
<redisConfiguration namespacePrefix="opensai" />

<simvizConfiguration worldFilePath="${TUTORIALS_WORLD_FILES_FOLDER}/1_pendulum_world.urdf">
</simvizConfiguration>
```

## Adding an end effector to the pendulum

We will first modify the pendulum urdf model to add a sphere at the end effector. There are two ways of doing it:

#### 1 - Add a second visual element to the link1

Let's add a second visual element to the link1 in order to put a sphere at the end of the pendulum. The visual element needs a geometry tag. Try to do it yourself in the pendulum.urdf file. The pendulum cylinder is 1m long and has radius 7cm.

<details>
<summary>Hint</summary>
You can draw inspiration from the visual element for the sphere in the base_link. remember that the origin of the visual element is defined with respect to the parent joint (located at the top sphere in this example)
</details>

<details>
  <summary>Solution</summary>
  
  Here is the block to add just after the existing visual element of link1

```
<visual>
	<origin xyz="0.0 0.0 -1.0" rpy="0 0 0" />
	<geometry>
		<sphere radius="0.1" />
	</geometry>
</visual>
```
</details>

#### 2 - Add a link connected via a fixed joint to link1

This is the preffered way of doing in case the added visual also has a corresponding collision element because OpenSai does not suppoer multiple collision elements on the same link.

<details>
<summary>Hint</summary>
The link needs a unique name, an inertial element and a visual element.

Remember to set the type of the joint to fixed, to set its parent and child elements to the correct names.

You have a 1m translation to set somewhere. It can be set either in the fixed joint, or in the visual element of the new link. We recommend setting it in the joint location.
</details>

<details>
<summary>Solution</summary>

Here is the link to add after link1
```
<link name="link1_sphere">
	<inertial>
		<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
		<mass value="0.001" />
		<inertia ixx="0.001" iyy="0.001" izz="0.001" ixy="0" ixz="0" iyz="0" />
	</inertial>
	<visual>
		<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
		<geometry>
			<sphere radius="0.1" />
		</geometry>
	</visual>
</link>
```
Here is the joint to add after j1
```
<joint name="j1_fixed" type="fixed">
	<parent link="link1" />
	<child link="link1_sphere" />
	<origin xyz="0 0 -1"/>
</joint>
```

</details>

In both cases, you can start the simulation and it should now liik like the following:

![](images/1_bot_sphere_added.png)

## Changing colors

In order to have a more visually pleasing experience, you can change the color of the visual elements by adding a `material` tag next to the `geometry` tag.
Replace the visual element of the base_link by the following to get a blue sphere on top:
```
<visual>
	<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
	<geometry>
		<sphere radius="0.1" />
	</geometry>
	<material name="blue">
		<color rgba="0.0 0.0 1.0 1.0" />
	</material>
</visual>
```

Now try to make the bottom sphere red by yourself.

<details>
<summary>Solution</summary>

Replace the visual element of the bottom sphere by
```
<visual>
	<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
	<geometry>
		<sphere radius="0.1" />
	</geometry>
	<material name="red">
		<color rgba="1.0 0.0 0.0 1.0" />
	</material>
</visual>
```
</details>

Start the simulation, it should now look like
![](images/1_color_changed.png)

## Make gravity act on the pendulum
As mentioned before, the world file defines the world gravity, set to -9.81 in the vertical direction here. However it does not affect the pendulum. This is because the simulation implements gravity compensation for the robot models by default. The reason for that is that when using an actual robot arm, gravity compensation is in general already habdled internally by the robot, and the controller we implement should therefore not perform gravity compensation. So we want our controller in simulation not to have to do gravity compensation either.

In order to let the simulation know that we don't want it to do the robot gravity compensation, we will need to modify the OpenSai config file `tuto_config_folder/xml_files/1_pendulum.xml`. and add the following inside the `simvizConfiguration` tag:
```
<simParameters enableGravityCompensation="false" />
```

After doing it, start the simulation again, move the pendulum to one side and you should see it oscillate.

## Make a double pendulum
Let us now modify the urdf file to make a double pendulum. You need to add a link and a joint to the existing model. Let's make the intermediate joints blue and the end effector red.

<details>
<summary>Solution</summary>

Here is a proposed urdf file using fixed joints and one visual element per link:
```
<?xml version="1.0" ?>

<robot name="pendulum">

	<link name="base_link">
		<inertial>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<mass value="1" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<geometry>
				<sphere radius="0.1" />
			</geometry>
			<material name="blue">
				<color rgba="0.0 0.0 1.0 1.0" />
			</material>
		</visual>
	</link>
	<link name="link1">
		<inertial>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<mass value="1.0" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<geometry>
				<cylinder radius="0.07" length="1" />
			</geometry>
		</visual>
	</link>
	<link name="link1_sphere">
		<inertial>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<mass value="0.001" />
			<inertia ixx="0.001" iyy="0.001" izz="0.001" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<geometry>
				<sphere radius="0.1" />
			</geometry>
			<material name="blue"/>
		</visual>
	</link>
	<link name="link2">
		<inertial>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<mass value="1.0" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<geometry>
				<cylinder radius="0.07" length="1" />
			</geometry>
		</visual>
	</link>
	<link name="link2_sphere">
		<inertial>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<mass value="0.001" />
			<inertia ixx="0.001" iyy="0.001" izz="0.001" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<geometry>
				<sphere radius="0.1" />
			</geometry>
			<material name="red">
				<color rgba="1.0 0.0 0.0 1.0" />
			</material>
		</visual>
	</link>

	<joint name="j1" type="revolute">
		<parent link="base_link" />
		<child link="link1" />
		<origin xyz="0 0 0"/>
		<axis xyz="1 0 0" />
		<limit lower="-2.967" upper="2.967" effort="176" velocity="1.7104" />
	</joint>
	<joint name="j1_fixed" type="fixed">
		<parent link="link1" />
		<child link="link1_sphere" />
		<origin xyz="0 0 -1"/>
	</joint>
	<joint name="j2" type="revolute">
		<parent link="link1_sphere" />
		<child link="link2" />
		<origin xyz="0 0 0"/>
		<axis xyz="1 0 0" />
		<limit lower="-2.967" upper="2.967" effort="176" velocity="1.7104" />
	</joint>
	<joint name="j2_fixed" type="fixed">
		<parent link="link2" />
		<child link="link2_sphere" />
		<origin xyz="0 0 -1"/>
	</joint>

</robot>
```

Here is a proposed urdf file using several visual elements per link
```
<?xml version="1.0" ?>

<robot name="pendulum">

	<link name="base_link">
		<inertial>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<mass value="1" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
			<geometry>
				<sphere radius="0.1" />
			</geometry>
			<material name="blue">
				<color rgba="0.0 0.0 1.0 1.0" />
			</material>
		</visual>
	</link>
	<link name="link1">
		<inertial>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<mass value="1.0" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<geometry>
				<cylinder radius="0.07" length="1" />
			</geometry>
		</visual>
		<visual>
			<origin xyz="0.0 0.0 -1.0" rpy="0 0 0" />
			<geometry>
				<sphere radius="0.1" />
			</geometry>
			<material name="blue" />
		</visual>
	</link>
	<link name="link2">
		<inertial>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<mass value="1.0" />
			<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
		</inertial>
		<visual>
			<origin xyz="0.0 0.0 -0.5" rpy="0 0 0" />
			<geometry>
				<cylinder radius="0.07" length="1" />
			</geometry>
		</visual>
		<visual>
			<origin xyz="0.0 0.0 -1.0" rpy="0 0 0" />
			<geometry>
				<sphere radius="0.1" />
			</geometry>
			<material name="red">
				<color rgba="1.0 0.0 0.0 1.0" />
			</material>
		</visual>
	</link>

	<joint name="j1" type="revolute">
		<parent link="base_link" />
		<child link="link1" />
		<origin xyz="0 0 0"/>
		<axis xyz="1 0 0" />
		<limit lower="-2.967" upper="2.967" effort="176" velocity="1.7104" />
	</joint>
	<joint name="j2" type="revolute">
		<parent link="link1" />
		<child link="link2" />
		<origin xyz="0 0 -1"/>
		<axis xyz="1 0 0" />
		<limit lower="-2.967" upper="2.967" effort="176" velocity="1.7104" />
	</joint>

</robot>
```
</details>

Start the simulation and you will see:
![](images/1_double_pendulum.png)

Notice how the camera placement does not allow to see the full pendulum. Let's change it. You can make the camera position in the world file to `<position xyz="4.0 0.0 0.0" />` instead of `<position xyz="3.0 0.0 0.0" />` and you should now see:
![](images/1_double_pendulum_new_cam.png)

## Add an initial joint configuration
OpenSai provides the ability to define initial joint configurations from the urdf file directy by using the `callibration` tag of urdf joints (which is not intended for that purpose when using an irdf file with systems other that OpenSai).
You can give a value in radians using the rising attribute, or in degrees using the falling attribute. For prismatic joints, thr rising or falling field can be used and the value is in meters.

For example, add this to the first revolute joint `<calibration rising="0.5" />` and this to the second `<calibration falling="35.0" />` and the double pendulum will now start in the following configuration when starting the simulation

![](images/1_initial_config.png)

## Joint limits and damping
You can modify the joint limits in the urdf file directly. The simulation will by default enforce joint limits on the robots. The current joint limits for the two revolute joints are `-2.967` and `2.967` for the min position and max position respectively. Change them to `-0.967` and `0.967`, start the simulation and try to drag the pendulum to one side, you will see the simulation blocking the joint to their limits:
![](images/1_lower_joint_limits.png)

You can tell the simulation to not enforce the joint limits by adding the attribute `enableJointLimits="false"` next to `enableGravityCompensation="false"` in the xml config file in the `simParameters` element. Try:

```
<simParameters enableGravityCompensation="false"
	enableJointLimits="false" />
```

and you will see that the simulation does not enforce the joint limits anymore.

You can also add joint damping by adding to each joint a new tag: `<dynamics damping="0.5"/>`. You can select whichever positive calue for the joint damping per joint. Add a damping of 0.5 to both revolute joints in the urdf file, start the simulation and you should see the oscillations slowly stop.

## Adding objects to the world

You can add objects in the world file. There are 2 types of objects:
- Static objects (defined by the html tag `<static_object>`) are objects that cannot move
- Dynamic objects (defined by the html tag `<dynamic_object>`) are objects that can move in 6 dimensions in space (translations and rotations).

Both these objects can have an origin tag, the dynamic object must have an inertial tag, and can have a visual and collision tag. Let us add a floor to the world below the pendulum. You can add the following to the world file:

```
<static_object name="Floor">
	<origin xyz="0.0 0.0 -2.25" rpy="0 0 0" />
	<visual>
		<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
		<geometry>
			<box size="5.0 5.0 0.1" />
		</geometry>
		<material name="material_blue">
			<color rgba="0.0 0.1 0.5 1.0" />
		</material>
	</visual>
	<collision>
		<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
		<geometry>
			<box size="5.0 5.0 0.1" />
		</geometry>
	</collision>
</static_object>
```

Now try to add a box of side 15cm as a dynamic object to the world, initially at the location `0.0 0.7 -2.0`. Don't forget the inertial properties.

<details>
<summary>Solution</summary>

Add the following to the world file
```
<dynamic_object name="Box">
	<origin xyz="0.0 0.7 -2.0" rpy="0 0 0" />
	<inertial>
		<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
		<mass value="1" />
		<inertia ixx="0.1" iyy="0.1" izz="0.1" ixy="0" ixz="0" iyz="0" />
	</inertial>
	<visual>
		<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
		<geometry>
			<box size="0.15 0.15 0.15" />
		</geometry>
		<material name="material_green">
			<color rgba="0.0 0.5 0.1 1.0" />
		</material>
	</visual>
	<collision>
		<origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
		<geometry>
			<box size="0.15 0.15 0.15" />
		</geometry>
	</collision>
</dynamic_object>
```
</details>

Start the simulation, and you will see the box falling on the floor.
![](images/1_floor_box.png)
You can interact with the box using right click and drag it around. Use the mouse wheel to pull the box out of the screen or push it inside the screen.

You will notice that the box goes through the pendulum. This is because there are no collision elements to the robot links in the urdf. You can add them and test the interactions.

## Using the webui

Open a web browser and navigate to localhost:8000. If you see a message saying unable to connect, you may have to start the webui manually from the root OpenSai folder:

```
python bin/ui/server.py tutorials/tuto_config_folder/xml_files/webui_generated_file/webui.html
```

You should see the following:
![](images/1_webui.png)

You can explore the different exposed simulation parameters for the pendulum and the box. The details are explained in the OpenSai documentation.

## Plotting the joint angles in real time

Open a new online plot tab using the blue bitton on top of the webui and you will see a new tab appearing. In the search box marked 'select y key' look for the pendulum joint positions key called `sai::sensors::pendulum::joint_positions`. You can type joint_positions in the search bar and it will appear. Press the start button and the plot starts appearing.

![](images/1_online_plot.png)

## Recording and plotting the joint angles offline

You can also record data and plot it later. Click the SimViz logging button to turn it to ON on the left of the webui interface, and perturbate the pendulum. After a few seconds, press it again to stop the logging. You can now open the offline CSV plotter using the green button on the top of the webui.

![](images/1_offline_plotter.png)

Click the `Load CSV` button and navigate the the `log_files/simviz` folder, and open the `pendulum_simviz__<timestamp>.csv` file. Close the data you want to plot and click the button to open a new browser window with the graph.

You can specify the logging data frequency, folder path and other options in the xml config file. See the full documentation for more information.

## Next tutorial
[Controlling a robot arm](2_robot_arm.md)