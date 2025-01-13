#!/bin/bash
if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi

# Set the config file from the first command-line argument
# if [ "$#" -eq 0 ]; then
# 	config_file="1_pendulum.xml"
if [ "$#" -eq 1 ]; then
	if [ "$1" -eq "1" ]; then
		config_file="1_pendulum.xml"
	# elif [ "$1" -eq "2" ]; then
	# 	config_file="2_panda.xml"
	# elif [ "$1" -eq "3" ]; then
	# 	config_file="3_panda_haptic.xml"
	else
		echo "Invalid tutorial number. Please enter 1, 2 or 3."
		exit 1
	fi
else
	echo "Usage: $0 [tutorial number]"
	exit 1
fi

# launch redis server if not launched
if [ -z "$(pgrep redis-server)" ]; then
	redis-server &
	REDIS_PID=$!
fi

sleep 0.2

# launch sai main program
./bin/Tutorials_SAI "$config_file" &
SAI_MAIN_PID=$!

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
    kill -2 $SAI_MAIN_PID
}

sleep 1

# Launch interfaces server using tmux
tmux new-session -d -s interfaces_server "python3 bin/ui/server.py config_folder/xml_config_files/webui_generated_file/webui.html"

# Wait for SAI main program to quit and stop redis
wait $SAI_MAIN_PID
if [ ! -z "$REDIS_PID" ]; then
	kill -2 $REDIS_PID
fi

# Once SAI main program dies, kill interfaces server
tmux send-keys -t interfaces_server C-c

# Close the tmux session
tmux kill-session -t interfaces_server

# sleep for everything to close
sleep 0.5