#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m' # Reset to default color

# Set options to exit on error and unset variables
set -e
set -u

# install core libraries
mkdir -p core
cd core

# clone all repositories if needed
if [ ! -d "sai2-common" ]; then
    git clone https://github.com/manips-sai-org/sai2-common.git
fi
if [ ! -d "sai2-urdfreader" ]; then
    git clone https://github.com/manips-sai-org/sai2-urdfreader.git
fi
if [ ! -d "sai2-model" ]; then
    git clone https://github.com/manips-sai-org/sai2-model.git
fi
if [ ! -d "chai3d" ]; then
    git clone https://github.com/manips-sai-org/chai3d.git
fi
if [ ! -d "sai2-graphics" ]; then
    git clone https://github.com/manips-sai-org/sai2-graphics.git
fi
if [ ! -d "sai2-simulation" ]; then
    git clone https://github.com/manips-sai-org/sai2-simulation.git
fi
if [ ! -d "sai2-primitives" ]; then
    git clone https://github.com/manips-sai-org/sai2-primitives.git
fi
if [ ! -d "sai2-interfaces" ]; then
    git clone https://github.com/manips-sai-org/sai2-interfaces.git
fi

# echo "Cloned all repositories."
echo "${YELLOW}${BOLD}All repositories successfully cloned (or cloning was not needed)${RESET}"
sleep 0.5

# build all the repositories
cd sai2-common
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai2-common successfully built${RESET}"
sleep 0.5

cd sai2-urdfreader
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai2-urdfreader successfully built${RESET}"
sleep 0.5

cd sai2-model
cd rbdl
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai2-model successfully built${RESET}"
sleep 0.5

cd chai3d
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}chai3d successfully built${RESET}"
sleep 0.5

cd sai2-graphics
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai2-graphics successfully built${RESET}"
sleep 0.5

cd sai2-simulation
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai2-simulation successfully built${RESET}"
sleep 0.5

cd sai2-primitives
cd ruckig
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai2-primitives successfully built${RESET}"
sleep 0.5

cd sai2-interfaces
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ..
echo "${YELLOW}${BOLD}sai2-interfaces successfully built${RESET}"
pip3 install -r ui/requirements.txt
echo "${YELLOW}${BOLD}sai2-interfaces python requirements installed${RESET}"
sleep 0.5

cd ..
echo "${GREEN}${BOLD}All repositories successfully built. The main Opensai application can be built${RESET}"
