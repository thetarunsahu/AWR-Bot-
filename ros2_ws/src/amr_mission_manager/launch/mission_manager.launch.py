"""Launch the standalone warehouse mission manager with its inventory."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    """Expose inventory and clock options without any navigation dependency."""
    inventory_path = (
        Path(get_package_share_directory('amr_mission_manager'))
        / 'config' / 'inventory.yaml'
    )
    return LaunchDescription([
        DeclareLaunchArgument(
            'inventory_file',
            default_value=str(inventory_path),
            description='Path to warehouse inventory YAML.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use /clock when an external simulator provides it.',
        ),
        Node(
            package='amr_mission_manager',
            executable='mission_manager',
            name='mission_manager',
            output='screen',
            parameters=[{
                'inventory_file': ParameterValue(
                    LaunchConfiguration('inventory_file'), value_type=str,
                ),
                'use_sim_time': ParameterValue(
                    LaunchConfiguration('use_sim_time'), value_type=bool,
                ),
            }],
        ),
    ])
