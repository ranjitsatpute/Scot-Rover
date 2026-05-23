# instruction manual for the compiler. It tells ROS 2 exactly which files to  /
#turn into a program and which dependencies (like SciPy) to link together.
cmake_minimum_required(VERSION 3.8)
project(libs_rover_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# instruction manual for the compiler. It tells ROS 2 exactly which files to  /
#turn into a program and which dependencies (like SciPy) to link together.

# Generate custom messages and services
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SpectrumData.msg"
  "msg/ElementResult.msg"
  "msg/AnalysisResult.msg"
  "srv/TriggerMeasurement.srv"
  DEPENDENCIES std_msgs builtin_interfaces
)

# Install Python modules
ament_python_install_package(libs_rover)

# Install Python nodes
install(PROGRAMS
  libs_rover/libs_sensor_simulator_node.py
  libs_rover/spectrum_analyzer_node.py
  libs_rover/measurement_controller_node.py
  libs_rover/backend_monitor_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install config files
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
