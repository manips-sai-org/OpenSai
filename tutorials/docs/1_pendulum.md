## Tutorial 1 - Simulation with pendulums

This tutorial aims at showcasing the main features of SAI when defining a simulation world. All the tutorial files are present in the `tutorials` folder.

A very basic and uncomplete simulation is provided. Following this tutorial, you will learn how to complete the roboti model, add things to the simulation and interact with it.

First, launch the first tutorial. From the root folder of the SAI repository:
```
sh scripts/tutorial_launch.sh 1
```

You should see a window opening, showing two spheres on a black background:
[](images/1_initial_simulation.png)

Those spheres represent a simple pendulum, hanging vertically, but the link between the pendulums is not represented yet. there are already a few things that you can do with this simulation:
- move, zoom and unzoom the camera using the mouse (scrolling wheel, left click + drag, center click + drag, crtl + left click + drag, shift + left click + drag, arrow keys, A or Z keys)
- interact with the pendulum by right clicking on the bottom sphere and dragging it left or right

Note that the gravity seems not to afect the pendulum. We will change this soon.