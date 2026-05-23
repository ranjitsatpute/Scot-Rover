from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='libs_rover_pkg',
            executable='libs_sensor_simulator_node.py',
            name='libs_sensor_simulator',
            output='screen',
            parameters=[{'database_file': 'spectral_database.yaml'}]
        ),
        Node(
            package='libs_rover_pkg',
            executable='spectrum_analyzer_node.py',
            name='spectrum_analyzer',
            output='screen'
        ),
        Node(
            package='libs_rover_pkg',
            executable='measurement_controller_node.py',
            name='measurement_controller',
            output='screen'
        )
    ])
