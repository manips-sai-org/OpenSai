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
if [ ! -d "sai-common" ]; then
    git clone https://github.com/manips-sai-org/sai-common.git
fi
if [ ! -d "sai-urdfreader" ]; then
    git clone https://github.com/manips-sai-org/sai-urdfreader.git
fi
if [ ! -d "sai-model" ]; then
    git clone https://github.com/manips-sai-org/sai-model.git
fi
if [ ! -d "chai3d" ]; then
    git clone https://github.com/manips-sai-org/chai3d.git
fi
if [ ! -d "sai-graphics" ]; then
    git clone https://github.com/manips-sai-org/sai-graphics.git
fi
if [ ! -d "sai-simulation" ]; then
    git clone https://github.com/manips-sai-org/sai-simulation.git
fi
if [ ! -d "sai-primitives" ]; then
    git clone https://github.com/manips-sai-org/sai-primitives.git
fi
if [ ! -d "sai-interfaces" ]; then
    git clone https://github.com/manips-sai-org/sai-interfaces.git
fi

# echo "Cloned all repositories."
echo "${YELLOW}${BOLD}All repositories successfully cloned (or cloning was not needed)${RESET}"
sleep 0.5

# build all the repositories
cd sai-common
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai-common successfully built${RESET}"
sleep 0.5

cd sai-urdfreader
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai-urdfreader successfully built${RESET}"
sleep 0.5

cd sai-model
cd rbdl
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai-model successfully built${RESET}"
sleep 0.5

cd chai3d
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}chai3d successfully built${RESET}"
sleep 0.5

cd sai-graphics
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai-graphics successfully built${RESET}"
sleep 0.5

cd sai-simulation
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai-simulation successfully built${RESET}"
sleep 0.5

cd sai-primitives
cd ruckig
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ../..
echo "${YELLOW}${BOLD}sai-primitives successfully built${RESET}"
sleep 0.5

cd sai-interfaces
mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -j4 && cd ..
echo "${YELLOW}${BOLD}sai-interfaces successfully built${RESET}"
pip3 install -r ui/requirements.txt
echo "${YELLOW}${BOLD}sai-interfaces python requirements installed${RESET}"
sleep 0.5

cd ..
echo "${GREEN}${BOLD}All repositories successfully built. The main OpenSai application can be built${RESET}"
