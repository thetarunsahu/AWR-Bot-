from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    slam_share = get_package_share_directory("slam_toolbox")
    nav_share = get_package_share_directory("amr_navigation")
    params_file = os.path.join(nav_share, "config", "slam.yaml")
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(slam_share, "launch", "online_async_launch.py")),
        launch_arguments={"slam_params_file": params_file, "use_sim_time": "true"}.items(),
    )
    return LaunchDescription([slam])
