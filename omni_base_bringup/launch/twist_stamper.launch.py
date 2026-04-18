import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    twist_stamper_node = Node(
        package='omni_base_bringup',
        executable='twist_stamper_node',
        name='twist_stamper',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    
    return LaunchDescription([twist_stamper_node])
