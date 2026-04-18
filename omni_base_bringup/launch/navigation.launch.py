import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # --- Paths ---
    omni_bringup_dir = get_package_share_directory('omni_base_bringup')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    nav2_simple_dir = get_package_share_directory('nav2_simple_navigation')
    
    # Absolute path to map directoryf
    part_mapping_dir = '/home/huylake/ros2_ws/src/omni_based_robot/part_mapping_robot'

    # --- Configurations ---
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_yaml_file = LaunchConfiguration('map', default=os.path.join(part_mapping_dir, 'hospital_full_map.yaml'))
    params_file = LaunchConfiguration('params_file', default=os.path.join(omni_bringup_dir, 'config', 'nav2', 'nav2_params.yaml'))
    ekf_params_file = os.path.join(nav2_simple_dir, 'config', 'ekf.yaml')

    # --- Nodes ---
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[params_file, {'yaml_filename': map_yaml_file}, {'use_sim_time': use_sim_time}]
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]
    )

    lifecycle_localization = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['map_server', 'amcl']}]
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]
    )

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}]
    )

    lifecycle_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time,
                     'autostart': True,
                     'node_names': ['planner_server', 'controller_server', 'behavior_server', 'bt_navigator']}]
    )

    # Delay navigation nodes to allow map_server and AMCL to start
    delayed_planner_server = TimerAction(period=10.0, actions=[planner_server])
    delayed_controller_server = TimerAction(period=10.0, actions=[controller_server])
    delayed_behavior_server = TimerAction(period=10.0, actions=[behavior_server])
    delayed_bt_navigator = TimerAction(period=10.0, actions=[bt_navigator])
    delayed_lifecycle_navigation = TimerAction(period=10.0, actions=[lifecycle_navigation])

    rviz_config_file = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('map', default_value=map_yaml_file),
        DeclareLaunchArgument('params_file', default_value=params_file),
        map_server,
        amcl,
        lifecycle_localization,
        delayed_planner_server,
        delayed_controller_server,
        delayed_behavior_server,
        delayed_bt_navigator,
        delayed_lifecycle_navigation,
        rviz_node
    ])