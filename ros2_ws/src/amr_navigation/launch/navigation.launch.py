from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    nav2_share = get_package_share_directory("nav2_bringup")
    amr_nav_share = get_package_share_directory("amr_navigation")
    params_file = os.path.join(amr_nav_share, "config", "nav2_params.yaml")
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_share, "launch", "navigation_launch.py")),
        launch_arguments={"use_sim_time": "true", "params_file": params_file, "autostart": "true", "use_composition": "False"}.items(),
    )
    target_bridge = Node(
        package="amr_navigation",
        executable="target_pose_nav2_bridge.py",
        name="target_pose_nav2_bridge",
        output="screen",
        parameters=[{"use_sim_time": True}],
    )
    return LaunchDescription([nav2, target_bridge])
