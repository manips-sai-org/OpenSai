# Tutorial 3 - Controlling a robot arm with a haptic device

In this tutorial, we add a haptic controller for controlling the robot end effector. You will need access to a haptic device compatible with chai3d for this tutorial.

First, install and test the [chai3d OpenSai haptic device driver](https://github.com/manips-sai-org/chaiHapticdeviceRedisDriver)

Once the driver is working, you can take a look at the xml configuration file for the third tutorial called `3_robot_arm_haptic.xml`. There is a new tag in the file to define the haptic controller:

```
<hapticDeviceControlConfiguration controlMode="impedance"
	switchFunction="clutch"
	switchUsageType="click"
	orientationTeleopEnabled="false">

	<controlledRobotTask robotName="Panda"
		controllerName="cartesian_controller"
		taskName="cartesian_task" />

	<logger logFolderName="log_files/tuto_3/haptic_controllers" />

	<impedanceMode>
		<scalingFactors linear="1.0"/>
		<forceFeedback reductionFactorForce="0.1" />
	</impedanceMode>
</hapticDeviceControlConfiguration>
```

Some explanation about those elements:
- The `hapticDeviceControlConfiguration` tag sets up a haptic controller for one haptic device. The attributes we show here are:
	- controlMode: can be "impedance" or "admittance". We will try both in this tutorial
	- switchFunction: can be "clutch" or "orientationControl". This defined the function of the switch. That is to saw, what happens if the switch is clicked or held. It can either put the device in clutch mode (haptic device moves freely without affecting the robot), or switch between translation only and translation plus orientation control.
	- switchUsage: can be "click" or "hold". This defines if the switch is activated/deactivated by clicking/clicking or by holding/releasing it.
	- orientationTeleopEnabled: defined if the orientation teleoperation is enabled by default or not
- The `controlledRobotTask` tag is mandatory and all its attributes must correspond with the controller definition of the task we want to control haptically. The controlled task must be a motion force task.
- The `logger` tag is similar to the one in the simviz and controller configurations
- The `impedanceMode` tag defines additional parameters specific to the impedance mode. Here, we show the scaling factor and the force reduction factor.

Launch the haptic device driver, and then launch the third tutorial:
```
ah scripts/tutorial_launch.sh 3
```

You will see the same scene as tutorial 2 start in simulation.
At the same time, your haptic device will move to the center of its workspace.
Press the switch or gripper of your haptic device to start the control. You will have haptic control of the position of the simulated robot end effector. When you click on the switch, it will alternate between haptic control and clutch mode. If you try and go youch the tilted table, you should feel some force feedback on the haptic device. If the feedback is too small, increase the force reduction factor in the xml config file. If the force is too large and causes oscillations of the device, decrease the force reduction factor.

## Admittance control

In the configuration file, switch the controlMode to "admittance", and start the application again. Press the switch of the haptic device and you can start controlling the robot in admittance mode. If you push in one direction of the haptic device, it will command the robot to move in that direction at a speed proportional to the pushing force.

## Orientation control

If your haptic device has 6 degrees of freedom, you can control the orientation of the robot as well.
Go back to the impedance mode, and change the switch function from "clutch" to "orientationControl" and the switch usage type from "click" to "hold". Start the tutorial again, press the switch to enable teleoperation. In this configuration, you can control orientation by holsing the switch and rotating the haptic device handle.

## Plane constraint

Add the following line inside the `hapticDeviceControlConfiguration` tag:
```
<planeGuidance enabled="true" />
```

Start the tutorial program, enable teleoperation by pressing the haptic device switch and you should that both the haptic device and robot are constrained to moving in the horizontal plane.

For more information about all the parametrizable elements in the haptic controllers, look at the OpenSai documentation.