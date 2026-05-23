# ROS 2 Humble base image
FROM ros:humble
#----------------------------------------------------

# Set environment variables
# Prevents interactive prompts during apt install
# Required for automated builds
ENV DEBIAN_FRONTEND=noninteractive 
#Prevents ROS nodes from accidentally communicating with other networks
ENV ROS_DOMAIN_ID=0
#----------------------------------------------------

# Install system dependencies
#You’re installing:
#colcon → ROS build system
#rclpy → Python ROS 2 client library
#std_msgs → Basic ROS message types
#rosidl → Message/service generation

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-rclpy \
    ros-humble-std-msgs \
    ros-humble-rosidl-default-generators \
    ros-humble-rosidl-default-runtime \
    && rm -rf /var/lib/apt/lists/*
#----------------------------------------------------
#These libraries support:
#Spectral signal processing (NumPy, SciPy)
#Visualization of LIBS spectra (Matplotlib)
#Configuration handling (YAML)
# Install Python dependencies
RUN pip3 install \
    numpy \
    matplotlib \
    pyyaml \
    scipy
#----------------------------------------------------

# Create workspace directory
WORKDIR /ros2_ws

# Copy source code
COPY src /ros2_ws/src
#----------------------------------------------------
# Build the workspace
#Source base ROS 2 environment
#Compile all packages inside src/
#Generate:
# build/
#install/
#symlink-install
#Enables faster development
#Code changes don’t require full rebuilds
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install
#----------------------------------------------------
# Source the workspace on container start
#Every time the container starts:
#ROS 2 environment is ready
#Workspace packages are available
#This eliminates environment setup errors and ensures immediate productivity.
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc
#----------------------------------------------------

# Set entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["bash"]
