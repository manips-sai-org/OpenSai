#!/bin/bash
if [ ! "$BASH_VERSION" ] ; then
    exec /bin/bash "$0" "$@"
fi

# Set the config file from the first command-line argument
config_file="$1"

# launch redis server is not launched
if [ -z "$(pgrep redis-server)" ]; then
	redis-server &
	REDIS_PID=$!
fi

sleep 0.2

# launch opensai main program
./bin/OpenSai_main config_folder "$config_file" &
OPENSAI_MAIN_PID=$!

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
    kill -2 $OPENSAI_MAIN_PID
}

sleep 1

# Launch interfaces server using tmux
tmux new-session -d -s interfaces_server "python3 bin/interface/server.py config_folder/main_configs/webui_generated_file/webui.html"

# Wait for OpenSai main program to quit and stop redis
wait $OPENSAI_MAIN_PID
if [ ! -z "$REDIS_PID" ]; then
	kill -2 $REDIS_PID
fi

# Once OpenSai main program dies, kill interfaces server
tmux send-keys -t interfaces_server C-c

# Close the tmux session
tmux kill-session -t interfaces_server

# sleep for everything to close
sleep 0.5