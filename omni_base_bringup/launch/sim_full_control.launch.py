import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    desc_pkg = get_package_share_directory('omni_base_description')
    bringup_pkg = get_package_share_directory('omni_base_bringup')
    ctrl_pkg = get_package_share_directory('omni_base_controller_configuration')

    # Bật Gazebo với world Hospital
    world_path = os.path.join(desc_pkg, 'worlds', 'hospital_full.world')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_path}'}.items(),
    )

    # Biến môi trường nạp yaml parameter cho Gazebo ros2_controlplugin 
    controller_config = os.path.join(get_package_share_directory('omni_base_description'), 'config', 'configuration.yaml')
    
    # Biến môi trường model paths cho Gazebo
    my_robot_gazebo_share = get_package_share_directory('my_robot_gazebo')
    omni_base_desc_share = get_package_share_directory('omni_base_description')
    gz_models_path = os.path.dirname(omni_base_desc_share) + ':' + os.path.join(omni_base_desc_share, 'models') + ':' + os.path.join(my_robot_gazebo_share, 'models')
    
    set_gz_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gz_models_path
    ) #

    # Nạp URDF và Robot State Publisher từ thư mục omni_base_description
    urdf_file = os.path.join(get_package_share_directory('omni_base_description'), 'urdf', 'base', 'omni_base.urdf')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read().replace('$$PARAMETERS_FILE$$', controller_config)

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}],
        output='screen'
    ) #

    # Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim', executable='create',
        arguments=['-topic', 'robot_description', '-name', 'omni_base', '-y', '10.0', '-z', '0.2', '-Y', '-1.5708'],
        output='screen'
    ) #
    delayed_spawn = TimerAction(
        period=25.0,
        actions=[spawn_robot]
    ) #
    # Load Controllers (Cần thời gian trễ sau khi robot xuất hiện)
    joint_state_broadcaster = Node(
        package='controller_manager', executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': True}],
    ) #
    mobile_base_controller = Node(
        package='controller_manager', executable='spawner',
        arguments=['mobile_base_controller', '--controller-manager', '/controller_manager'],
        parameters=[{'use_sim_time': True}],
    ) #
    
    delayed_controllers = TimerAction(
        period=4.0,
        actions=[joint_state_broadcaster, mobile_base_controller]
    ) #

    # ROS <-> Gazebo Bridge
    bridge_config = os.path.join(get_package_share_directory('omni_base_description'), 'config', 'bridge_config.yaml')
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config, 'use_sim_time': True}],
        output='screen'
    ) #

    # Include Twist Mux 
    twist_mux = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(bringup_pkg, 'launch', 'twist_mux.launch.py'))
    ) #

    return LaunchDescription([
        set_gz_path,
        gazebo,
        rsp,
        delayed_spawn,
        delayed_controllers,
        bridge,
        twist_mux
    ])