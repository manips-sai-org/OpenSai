#!/bin/bash

# checkout master and pull latest changes on all core repositories
cd core
cd sai2-common
git checkout master && git pull
cd ..

cd sai2-urdfreader
git checkout master && git pull
cd ..

cd sai2-model
git checkout master && git pull
cd ..

cd chai3d
git checkout master && git pull
cd ..

cd sai2-graphics
git checkout master && git pull
cd ..

cd sai2-simulation
git checkout master && git pull
cd ..

cd sai2-primitives
git checkout master && git pull
cd ..

cd sai2-interfaces
git checkout master && git pull
cd ..

