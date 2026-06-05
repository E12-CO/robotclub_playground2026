import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node

import xacro


def generate_launch_description():

    # Check if we're told to use sim time
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Process the URDF file
    pkg_path = os.path.join(get_package_share_directory('robotclub_playground2026'))
    xacro_file_r1 = os.path.join(pkg_path,'R1/description_r1','robot_r1.urdf.xacro')
    xacro_file_r2 = os.path.join(pkg_path,'R2/description_r2','robot_r2.urdf.xacro')
    robot_description_config_r1 = xacro.process_file(xacro_file_r1)
    robot_description_config_r2 = xacro.process_file(xacro_file_r2)

    # Create a robot_state_publisher node
    params_r1 = {'robot_description': robot_description_config_r1.toxml(), 'use_sim_time': use_sim_time}
    node_robot_state_publisher_r1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='r1',
        output='screen',
        parameters=[params_r1]
    )

    params_r2 = {'robot_description': robot_description_config_r2.toxml(), 'use_sim_time': use_sim_time}
    node_robot_state_publisher_r2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='r2',
        output='screen',
        parameters=[params_r2]
    )

    # Launch!
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use sim time if true'),

        node_robot_state_publisher_r1,
        node_robot_state_publisher_r2
    ])
