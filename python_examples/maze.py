import numpy as np
import time
import json
import math
from enum import Enum, auto
from dataclasses import dataclass
from scipy.spatial.transform import Rotation as R
import sys
import os
import yaml

black = "0.0 0.0 0.0 1.0"
green = "0.1 0.5 0.1 1.0"
blue = "0.0 0.1 0.5 1.0"
white = "1.0 1.0 1.0 1.0"
beige = "1.0 0.7 0.4 1"
orange = "1 0.3 0 1"
grey = "0.2 0.2 0.2 1.0"

def createBlocks(grid: list[list[str]] ) -> list[tuple[int, int, int, int]]:

    #Go to a point, check if you can expand in one direction, then do for the other

    explored = {}

    blockList = []

    if len(grid) == 0:
        return []

    for i in range(len(grid)):
        for j in range(len(grid[0])):

            if grid[i][j] != "x" or (i,j) in explored:
                continue

            startPoint = (i,j)

            col = j
            row = i

            while col < len(grid[0]) and grid[row][col] == "x" and (row, col) not in explored:
                col = col + 1

            row = row + 1

            while row < len(grid):
                goodRow = True
                for k in range(j, col):
                    if grid[row][k] != "x":
                        goodRow = False
                        break
                if goodRow == False:
                    break

                row = row+1


            endPoint = (row -1,col -1)

            for r in range(i, row):
                for c in range(j, col):
                    explored[(r,c)] = True

            blockList.append((startPoint[0], startPoint[1], endPoint[0], endPoint[1]))

    return blockList

#blocks are defined by center point, and lower height
def createBlocksTemplate(blockList: list[tuple[int, int, int, int]], maze_dims: tuple[int, int],  pos: tuple[float, float, float],  scale: tuple[float, float, float], color: str) -> str:

    blocks = ""

    xc,yc,zc = pos
    dx,dy,dz = scale
    x, y, z = (xc - maze_dims[0]*dx/2, yc - maze_dims[1]*dy/2, zc)

    for i in range(len(blockList)):

        blockR1 = blockList[i][0]
        blockC1 = blockList[i][1]
        blockR2 = blockList[i][2]
        blockC2 = blockList[i][3]

        #Assume that the input from the blocklist is non degenerate

        x1 = x + blockR1*dx
        y1 = y + blockC1*dy
        z1 = z

        w = (blockR2 - blockR1 + 1)*dx
        h = (blockC2 - blockC1 + 1)*dy

        x1 = round(x1, 3)
        y1 = round(y1, 3)
        z1 = round(z1, 3)

        w = round(w,3)
        h = round(h, 3)
        tall = dz

        wallPos = (x1, y1 , z1)
        dims = (w, h, tall)
        name = "mazewall-{}".format(i)

        blocks = blocks + createLLBlockTemplate("static", name, wallPos, dims, color, 1) + "\n\n"


    return blocks

def createBlockTemplate(btype: str, name: str , pos: tuple[float, float, float], dims: tuple[float, float, float], color: str, mass: float) -> str:

    box_org = "{} {} {}".format(pos[0], pos[1], pos[2])
    box_dims = "{} {} {}".format(dims[0], dims[1], dims[2])#assume dims is non degenerate

    block = """    <{}_object name=\"{}\">
        <origin xyz=\"{}\" rpy=\"0 0 0\" />
        <inertial>
            <origin xyz=\"0.0 0.0 0.0\" rpy=\"0 0 0\" />
            <mass value=\"{}\" />
            <inertia ixx=\"0.1\" iyy=\"0.1\" izz=\"0.1\" ixy=\"0\" ixz=\"0\" iyz=\"0\" />
        </inertial>
        <visual>
            <origin xyz=\"0.0 0.0 0.0\" rpy=\"0 0 0\" />
            <geometry>
                <box size=\"{}\" />
            </geometry>
            <material name=\"material_green\">
                <color rgba=\"{}\" />
            </material>
        </visual>
        <collision>
            <origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
            <geometry>
                <box size=\"{}\" />
            </geometry>
        </collision>
    </{}_object>""".format(btype, name, box_org, mass, box_dims, color, box_dims, btype)

    return block

def createLLBlockTemplate(btype: str, name: str, pos: tuple[float, float, float], dims: tuple[float, float, float], color: str, mass: float)->str:

    pos = changeOfCoordinatesBlock(pos, dims)

    return createBlockTemplate(btype, name, pos, dims, color, mass)

def createCylinderTemplate(ctype: str, name: str, pos: tuple[float, float, float], cdims: tuple[float,float], color: str) -> str:

    cyl_org = "{} {} {}".format(pos[0], pos[1], pos[2])

    cylinder = """    <{}_object name=\"{}\">
        <origin xyz=\"{}\" rpy=\"0 0 0\" />
        <inertial>
            <origin xyz=\"0.0 0.0 0.0\" rpy=\"0 0 0\" />
            <mass value=\"1\" />
            <inertia ixx=\"0.1\" iyy=\"0.1\" izz=\"0.1\" ixy=\"0\" ixz=\"0\" iyz=\"0\" />
        </inertial>
        <visual>
            <origin xyz=\"0.0 0.0 0.0\" rpy=\"0 0 0\" />
            <geometry>
                <cylinder radius=\"{}\" length=\"{}\"/>
            </geometry>
            <material name=\"material_green\">
                <color rgba=\"{}\" />
            </material>
        </visual>
        <collision>
            <origin xyz="0.0 0.0 0.0" rpy="0 0 0" />
            <geometry>
                <cylinder radius=\"{}\" length=\"{}\"/>
            </geometry>
        </collision>
    </{}_object>""".format(ctype, name, cyl_org, cdims[0], cdims[1], color, cdims[0], cdims[1], ctype)

    return cylinder

def createWorldTemplate(name: str, gravity: str)-> str:

    block = """<world name=\"{}\" gravity=\"{}\">""".format(name, gravity)
    
    return block

def createLightTemplate(name: str, type: str, position: str, lookat: str)->str:

    block = """    <light name=\"{}\" type=\"{}\">
        <position xyz=\"{}\" />
        <lookat xyz=\"{}\" />
    </light>""".format(name, type, position, lookat)

    return block

def createRobotTemplate(robotName: str, origin: tuple[float, float], dir: str, path: str) -> str:

    if robotName == "" or robotName[0].islower():
        return "nil"
    
    origin = "{} {} {}".format(origin[0], origin[1], origin[2])
    
    block = """    <robot name=\"{}\">
        <origin xyz="{}" rpy="0 0 0" />
        <model dir=\"{}\" path=\"{}\" name=\"{}\" />
    </robot>""".format(robotName, origin, dir, path, robotName.lower())

    return block

def createCameraTemplate(name: str, position : str, vertical: str, lookat: str):

    block = """    <camera name=\"{}\">
        <position xyz=\"{}\" />
        <vertical xyz=\"{}\" />
        <lookat xyz=\"{}\" />
    </camera>""".format(name, position, vertical, lookat)

    return block

#floor is always defined by center coordinates
def createFloorTemplate(name: str, pos: tuple[float, float, float], dims: tuple[float, float, float], color: str):

    floor = createBlockTemplate("static", name, pos, dims, color, 1)

    return floor + "\n\n"

def createTableTemplate(name: str, pos: tuple[float, float, float], table_dims: tuple[float, float], border: float, topthick: float, color: str)-> str:

    x, y, z = pos
    tr, th = table_dims

    pos = changeOfCoordinatesCylinder(pos, table_dims)
    base = createCylinderTemplate("static", name, pos, table_dims, color)

    top_pos = (x, y, z + th)

    top_dims = (tr + border, topthick)

    top_name = "{}-top".format(name)

    top_pos = changeOfCoordinatesCylinder(top_pos, top_dims)
    top = createCylinderTemplate("static", top_name, top_pos, top_dims, color)

    return base + "\n\n" + top + "\n\n"

def changeOfCoordinatesBlock(pos: tuple[float, float, float], dims: tuple[float, float, float])->tuple[float, float, float]:

    x,y,z = pos
    w,h,tall = dims
    
    xc = x + w/2
    yc = y + h/2
    zc = z + tall/2

    return (xc, yc, zc)

def changeOfCoordinatesCylinder(pos: tuple[float, float, float], cyl_dims: tuple[float, float])->tuple[float, float, float]:

    x, y, z = pos

    w,h = cyl_dims

    z = z + h/2

    return (x, y, z)
    

def createWorldFile(cfg: str):  

    data = {}

    with open(cfg, "r") as file:
        data = yaml.safe_load(file)

    maze = data['maze']
    blockList = createBlocks(maze)
    mazeDims = (len(maze), len(maze[0]))
    mazePos = data['mazePos']
    mazeScale = data['mazeScale']

    tablePos = data['tablePos']
    tableDims = data['tableDims']
    border = data['border']
    topthick = data['topthick']

    robotOrigin = data['robotOrigin']
    dogOrigin = data['dogOrigin']

    print("blockList = {}".format(blockList))

    with open(data['genfile'], "w") as file:

        file.write("<?xml version=\"1.0\" ?>\n\n")
        file.write(createWorldTemplate("test-world", "0.0 0.0 -9.81")+ "\n\n")
        file.write(createRobotTemplate("Panda", robotOrigin, "${ROBOT_FILES_FOLDER}", "mobile_base.urdf") + "\n\n")
        file.write(createRobotTemplate("Dog", dogOrigin, "${ROBOT_FILES_FOLDER}", "dog.urdf") + "\n\n")

        file.write(createTableTemplate("table", tablePos, tableDims, border, topthick, beige) + "\n\n")

        file.write(createFloorTemplate("floor", (0,0,-0.05), (5,5, 0.1), grey)+ "\n\n")

        file.write(createBlocksTemplate(blockList, mazeDims, mazePos, mazeScale, green)+"\n\n")
        
        file.write(createLightTemplate("light1", "directional", "2.0 -2.0 2.0", "0.0 0.0 0.5")+"\n\n")
        file.write(createLightTemplate("light2", "directional", "2.0 2.0 2.0", "0.0 0.0 0.5")+ "\n\n")
        file.write(createCameraTemplate("camera_fixed", "2.0 0.0 1.0", "0.0 0.0 1.0", "0.0 0.0 0.5") + "\n\n")

        file.write("</world>\n\n")

def main():

    createWorldFile("./mazecfg.yaml")

    pass
    

if __name__ == "__main__":
    main()

#Two things to do, generate robot embeddings
