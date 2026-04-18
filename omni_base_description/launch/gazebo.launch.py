from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import Command
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import SetEnvironmentVariable

import os

def generate_launch_description():

    description_pkg = get_package_share_directory('omni_base_description')

    xacro_file = os.path.join(
        description_pkg,
        'robots',
        'omni_base.urdf.xacro'
    )

    robot_description = Command(['xacro ', xacro_file])

    # Để đổi bản đồ, thay 'hospital_aws.world' thành 'hospital_full.world' bên dưới
    world_path = os.path.join(
        get_package_share_directory('omni_base_description'),
        'worlds',
        #'hospital_aws.world'  # Đổi thành 
        'hospital_full.world' 
    )
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_path],
        output='screen'
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description
        }]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'omni_base',
            '--x', '5.0',
            '--y', '10.0',
            '--yaw', '-1.5708',
        ],
        output='screen',
    )

    set_gz_resource_path = SetEnvironmentVariable(
    name='GZ_SIM_RESOURCE_PATH',
    value=[os.path.join(get_package_share_directory('omni_base_description'), 'models')]
)
    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot,
        set_gz_resource_path,
    ])
