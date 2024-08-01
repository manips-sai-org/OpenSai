
# install dependencies
os_name=$(uname -s)

if [ "$os_name" = "Linux" ]; then
    echo "Installing dependencies for linux."
	sudo apt-get update

	sudo apt-get install build-essential cmake git libeigen3-dev libtinyxml2-dev libgtest-dev python3-pip \
		libasound2-dev libusb-1.0.0-dev freeglut3-dev xorg-dev libglew-dev libglfw3-dev \
		libopenal-dev redis libhiredis-dev libjsoncpp-dev tmux

elif [ "$os_name" = "Darwin" ]; then
    echo "Installing dependencies for macOS."
	brew update
	brew install cmake git eigen tinyxml2 googletest glfw3 glew redis hiredis jsoncpp tmux openal-soft

else
    echo "ERROR: Unsupported OS. Only Linux and macOS are supported."
	exit 1
fi

echo "Dependencies installed."