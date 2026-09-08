"""Bring up the complete SIH26112 autonomous warehouse demo stack."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def include_launch(package: str, launch_file: str, launch_arguments=None):
    share = get_package_share_directory(package)
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(share, 'launch', launch_file)),
        launch_arguments=(launch_arguments or {}).items(),
    )


def generate_launch_description() -> LaunchDescription:
    headless = LaunchConfiguration('headless')
    use_rviz = LaunchConfiguration('rviz')

    simulation = include_launch(
        'amr_simulation',
        'sim.launch.py',
        {'headless': headless},
    )

    # Give Gazebo time to create the world, robot and ROS-GZ bridge before
    # starting nodes that depend on /scan, /odom and TF.
    slam = TimerAction(
        period=4.0,
        actions=[include_launch('amr_navigation', 'slam.launch.py')],
    )
    navigation = TimerAction(
        period=7.0,
        actions=[include_launch('amr_navigation', 'navigation.launch.py')],
    )
    mission_manager = TimerAction(
        period=9.0,
        actions=[
            include_launch(
                'amr_mission_manager',
                'mission_manager.launch.py',
                {'use_sim_time': 'true'},
            )
        ],
    )

    nav2_share = get_package_share_directory('nav2_bringup')
    rviz_config = os.path.join(nav2_share, 'rviz', 'nav2_default_view.rviz')
    rviz = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='screen',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': True}],
                condition=IfCondition(use_rviz),
            )
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'headless',
            default_value='true',
            description='Run Gazebo server-only; attach Gazebo GUI separately when desired.',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='false',
            description='Launch RViz2 using the Nav2 default visualization.',
        ),
        simulation,
        slam,
        navigation,
        mission_manager,
        rviz,
    ])
