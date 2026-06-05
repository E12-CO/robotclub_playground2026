import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

def generate_launch_description():
    package_name='robotclub_playground2026'
    
    world_path=os.path.join(get_package_share_directory(package_name), 'worlds/robot_playground.xml'),

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Run the spawner node from the gazebo_ros package. The entity name doesn't really matter if you only have a single robot.
    spawn_r1 = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'R1',
                                   '-x', '0.5', 
                                   '-y', '10.0',
                                   '-z', '0.10',
                                   '-Y', '0.0'                                   
                                  ],
                        namespace='r1',
                        output='screen')

    spawn_r2 = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'R2',
                                   '-x', '0.5', 
                                   '-y', '11.5',
                                   '-z', '0.10',
                                   '-Y', '0.0'                                   
                                  ],
                        namespace='r2',
                        output='screen')

    carto_map = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','carto_mapping.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Run the iRob_maneuv3r controller
    irob_maneuv3r_r1_instant = Node(
        package='irob_maneuv3r',
        executable='iRob_maneuv3r_tracker',
        name='irob_maneuv3r_r1',
        namespace = 'r1',
        output='screen',
        parameters=[os.path.join(get_package_share_directory(package_name), 'params_global', 'irob_maneuv3r_sim_r1.yaml')]
    )
    
    irob_maneuv3r_r2_instant = Node(
        package='irob_maneuv3r',
        executable='iRob_maneuv3r',
        #name='irob_maneu3r_r2',
        namespace = 'r2',
        output='screen',
        remappings=[
            ('cmd_vel_irob_auto', 'cmd_vel'),
            ],
        parameters=[os.path.join(get_package_share_directory(package_name), 'params_global', 'irob_maneuv3r_sim_r2.yaml')]
    )

    # Launch them all!
    return LaunchDescription([
        rsp, # Launch the Robot State Publisher
        ExecuteProcess(cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so',world_path], output='screen'),
        spawn_r1,
        carto_map,
        #spawn_r2,
        irob_maneuv3r_r1_instant,
        #irob_maneuv3r_r2_instant
    ])
