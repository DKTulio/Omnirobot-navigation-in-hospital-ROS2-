# Copyright (c) 2024 PAL Robotics S.L. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('omni_base_bringup')
    
    twist_mux_node = Node(
        package='twist_mux',
        executable='twist_mux',
        name='twist_mux',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'use_stamped': False},
            os.path.join(pkg_dir, 'config', 'twist_mux', 'twist_mux_topics.yaml'),
            os.path.join(pkg_dir, 'config', 'twist_mux', 'twist_mux_locks.yaml'),
            os.path.join(pkg_dir, 'config', 'twist_mux', 'joystick.yaml')
        ],
        remappings=[
            ('/cmd_vel_out', '/mobile_base_controller/cmd_vel_unstamped')
        ]
    )
    
    # Launch twist_stamper as a separate launch file
    twist_stamper_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', 'twist_stamper.launch.py'))
    )
    
    return LaunchDescription([
        twist_mux_node,
        twist_stamper_launch
    ])
