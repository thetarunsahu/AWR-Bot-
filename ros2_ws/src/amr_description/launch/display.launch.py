from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import xacro


def generate_launch_description():
    share = get_package_share_directory("amr_description")
    xacro_file = os.path.join(share, "urdf", "amr.urdf.xacro")
    robot_description = xacro.process_file(xacro_file).toxml()

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description}],
        ),
    ])
