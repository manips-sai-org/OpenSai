#!/bin/bash

if [ -d "core" ]; then
	cd core

	if [ -d "sai2-urdfreader" ]; then
		cd sai2-urdfreader
		rm -r build && cd ..
	fi

	if [ -d "sai2-common" ]; then
		cd sai2-common
		rm -r build && cd ..
	fi

	if [ -d "sai2-model" ]; then
		cd sai2-model/rbdl
		rm -r build && cd ..
		rm -r build && cd ..
	fi

	if [ -d "chai3d" ]; then
		cd chai3d
		rm -r build && cd ..
	fi

	if [ -d "sai2-graphics" ]; then
		cd sai2-graphics
		rm -r build && cd ..
	fi

	if [ -d "sai2-simulation" ]; then
		cd sai2-simulation
		rm -r build && cd ..
	fi

	if [ -d "sai2-primitives" ]; then
		cd sai2-primitives/ruckig
		rm -r build && cd ..
		rm -r build && cd ..
	fi

	if [ -d sai2-interfaces ]; then
		cd sai2-interfaces
		rm -r build && cd ..
	fi

	cd ..
fi

rm -r ~/.cmake/packages/SAI2-* && rm -r ~/.cmake/packages/CHAI3D