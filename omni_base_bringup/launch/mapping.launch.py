import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    bringup_pkg = get_package_share_directory('omni_base_bringup')
    desc_pkg = get_package_share_directory('omni_base_description')
    
    # Đường dẫn file tham số SLAM 
    slam_params_file = os.path.join(bringup_pkg, 'config', 'slam', 'mapper_params_online_sync.yaml')
    
    # Rviz config
    rviz_config_dir = os.path.join(desc_pkg, 'rviz', 'omni_base.rviz')

    return LaunchDescription([
        # Khởi chạy SLAM Toolbox
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_sync_launch.py')
            ),
            launch_arguments={
                'slam_params_file': slam_params_file,
                'use_sim_time': 'true'
            }.items()
        ),
        
        # Khởi chạy RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir, '--ros-args', '-p', 'use_sim_time:=true'],
            output='screen'
        )
    ])
