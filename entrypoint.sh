#!/bin/bash
# set up the necessary environment variables before executing whatever
# command you actually want to run
set -e

# Source ROS 2 setup
source /opt/ros/humble/setup.bash

# Source workspace if built
if [ -f /ros2_ws/install/setup.bash ]; then
    source /ros2_ws/install/setup.bash  # “The assembled and deployable robot brain” 
fi

exec "$@" # all arguments passed to the script.
