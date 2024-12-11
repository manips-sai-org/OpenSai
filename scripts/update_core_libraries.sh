#!/bin/bash

# checkout master and pull latest changes on all core repositories
cd core
cd sai-common
git checkout master && git pull
cd ..

cd sai-urdfreader
git checkout master && git pull
cd ..

cd sai-model
git checkout master && git pull
cd ..

cd chai3d
git checkout master && git pull
cd ..

cd sai-graphics
git checkout master && git pull
cd ..

cd sai-simulation
git checkout master && git pull
cd ..

cd sai-primitives
git checkout master && git pull
cd ..

cd sai-interfaces
git checkout master && git pull
cd ..

