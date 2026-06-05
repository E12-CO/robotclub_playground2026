# Launch file for ABU Robocon 2025 Robot
# Coded by TinLethax
import os

import launch
from launch.substitutions import LaunchConfiguration
import launch_ros.actions
import launch_ros.descriptions
import xacro

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

     # Specify the name of the package and path to xacro file within the package
    pkg_name = 'robotclub_playground2026'
    
    # Configure node launch information 
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    # Map resolution
    resolution = LaunchConfiguration('resolution', default='0.05')
    # Map publish period  
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')
    # Configuration file folder path
    configuration_directory = LaunchConfiguration('configuration_directory',default= os.path.join(get_package_share_directory(pkg_name), 'params_global') )
    # Configuration file
    configuration_basename = LaunchConfiguration('configuration_basename', default='R1_mapping_sim.lua')

    cartographer_node = launch_ros.actions.Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        namespace='r1',
        output='screen',
        remappings=[
            ('imu', 'imu/data_r1')
            ],
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-configuration_directory', configuration_directory,
                   '-configuration_basename', configuration_basename]
    )

    cartographer_occupancy_grid_node = launch_ros.actions.Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        namespace='r1',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-resolution', resolution, '-publish_period_sec', publish_period_sec]
    )

    # Cartographer SLAM
    delayed_slam_instant = launch.actions.TimerAction(period=3.0, actions=[cartographer_node, cartographer_occupancy_grid_node])


    return launch.LaunchDescription([
        cartographer_node,
        cartographer_occupancy_grid_node,
    ])
