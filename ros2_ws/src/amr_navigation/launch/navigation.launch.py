"""Launch only the Nav2 servers required for NavigateToPose on this AMR."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def nav2_node(package: str, executable: str, name: str, params_file: str, remappings=None):
    return Node(
        package=package,
        executable=executable,
        name=name,
        output='screen',
        parameters=[params_file],
        remappings=remappings or [],
    )


def generate_launch_description() -> LaunchDescription:
    amr_nav_share = get_package_share_directory('amr_navigation')
    params_file = os.path.join(amr_nav_share, 'config', 'nav2_params.yaml')

    controller = nav2_node(
        'nav2_controller', 'controller_server', 'controller_server', params_file
    )
    smoother = nav2_node(
        'nav2_smoother', 'smoother_server', 'smoother_server', params_file
    )
    planner = nav2_node(
        'nav2_planner', 'planner_server', 'planner_server', params_file
    )
    behaviors = nav2_node(
        'nav2_behaviors', 'behavior_server', 'behavior_server', params_file
    )
    bt_navigator = nav2_node(
        'nav2_bt_navigator', 'bt_navigator', 'bt_navigator', params_file
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'controller_server',
                'smoother_server',
                'planner_server',
                'behavior_server',
                'bt_navigator',
            ],
        }],
    )

    target_bridge = Node(
        package='amr_navigation',
        executable='target_pose_nav2_bridge.py',
        name='target_pose_nav2_bridge',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'max_retries': 1,
            'retry_delay_sec': 1.0,
            'goal_timeout_sec': 240.0,
            # RPP may rotate in place before translating on long aisle goals.
            # Keep this watchdog looser than the controller progress checker so
            # it does not cancel a healthy heading-alignment phase.
            'no_progress_timeout_sec': 85.0,
            'progress_epsilon_m': 0.05,
        }],
    )

    return LaunchDescription([
        controller,
        smoother,
        planner,
        behaviors,
        bt_navigator,
        lifecycle_manager,
        target_bridge,
    ])
