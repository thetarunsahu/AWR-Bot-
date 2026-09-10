from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def include(package: str, launch_file: str):
    share = get_package_share_directory(package)
    return IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(share, "launch", launch_file)))


def generate_launch_description():
    simulation = include("amr_simulation", "sim.launch.py")
    slam = TimerAction(period=4.0, actions=[include("amr_navigation", "slam.launch.py")])
    navigation = TimerAction(period=6.0, actions=[include("amr_navigation", "navigation.launch.py")])
    return LaunchDescription([simulation, slam, navigation])
