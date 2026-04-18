from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='teleop_twist_keyboard',
            executable='teleop_twist_keyboard',
            name='teleop_twist_keyboard',
            output='screen',
            prefix='xterm -e',  # Mở terminal riêng để nhập phím
            remappings=[
                ('/cmd_vel', '/key_vel')  # Đẩy ra topic key_vel để twist_mux xử lý
            ]
        )
    ])
