#!/bin/bash

if [ -d "core" ]; then
	cd core

	if [ -d "sai-urdfreader" ]; then
		cd sai-urdfreader
		rm -r build && cd ..
	fi

	if [ -d "sai-common" ]; then
		cd sai-common
		rm -r build && cd ..
	fi

	if [ -d "sai-model" ]; then
		cd sai-model/rbdl
		rm -r build && cd ..
		rm -r build && cd ..
	fi

	if [ -d "chai3d" ]; then
		cd chai3d
		rm -r build && cd ..
	fi

	if [ -d "sai-graphics" ]; then
		cd sai-graphics
		rm -r build && cd ..
	fi

	if [ -d "sai-simulation" ]; then
		cd sai-simulation
		rm -r build && cd ..
	fi

	if [ -d "sai-primitives" ]; then
		cd sai-primitives/ruckig
		rm -r build && cd ..
		rm -r build && cd ..
	fi

	if [ -d sai-interfaces ]; then
		cd sai-interfaces
		rm -r build && cd ..
	fi

	cd ..
fi

rm -r ~/.cmake/packages/SAI-* && rm -r ~/.cmake/packages/CHAI3D

rm -r build
rm -r bin