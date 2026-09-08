import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory("amr_description")
    simulation_share = get_package_share_directory("amr_simulation")
    ros_gz_sim_share = get_package_share_directory("ros_gz_sim")
    ros_gz_bridge_share = get_package_share_directory("ros_gz_bridge")

    xacro_file = os.path.join(description_share, "urdf", "amr.urdf.xacro")
    world_file = os.path.join(simulation_share, "worlds", "warehouse.sdf")
    bridge_file = os.path.join(simulation_share, "config", "bridge.yaml")
    robot_description = xacro.process_file(xacro_file).toxml()

    headless_arg = DeclareLaunchArgument(
        "headless",
        default_value="true",
        description="Run Gazebo server-only. Set false when a GUI display is available.",
    )
    headless = LaunchConfiguration("headless")

    gazebo_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": f"-r -s {world_file}"}.items(),
        condition=IfCondition(headless),
    )

    gazebo_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim_share, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": f"-r {world_file}"}.items(),
        condition=UnlessCondition(headless),
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}, {"use_sim_time": True}],
    )

    bridge = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_bridge_share, "launch", "ros_gz_bridge.launch.py")
        ),
        launch_arguments={
            "bridge_name": "amr_ros_gz_bridge",
            "config_file": bridge_file,
        }.items(),
    )

    spawn_robot = TimerAction(
        period=2.0,
        actions=[
            Node(
                package="ros_gz_sim",
                executable="create",
                output="screen",
                arguments=[
                    "-topic",
                    "robot_description",
                    "-name",
                    "sih26112_amr",
                    "-x",
                    "-10.0",
                    "-y",
                    "-7.5",
                    "-z",
                    "0.02",
                    "-allow_renaming",
                    "true",
                ],
            )
        ],
    )

    return LaunchDescription(
        [
            headless_arg,
            gazebo_headless,
            gazebo_gui,
            robot_state_publisher,
            bridge,
            spawn_robot,
        ]
    )
