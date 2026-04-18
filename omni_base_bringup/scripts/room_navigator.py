#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
import yaml
import sys
import math
import os
import time
import tf2_ros

class RoomNavigator(Node):
    def __init__(self):
        super().__init__('room_navigator')
        self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Load room data
        with open('/home/huylake/ros2_ws/src/omni_based_robot/omni_base_bringup/config/nav2/room_wait_points.yaml', 'r') as f:
            self.room_data = yaml.safe_load(f)['rooms']

        self.poses = []
        self.current_pose_index = 0
        self.status_file = '/home/huylake/ros2_ws/src/omni_based_robot/omni_base_bringup/config/nav2/status.txt'

        # TF for current pose
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

    def get_current_pose(self):
        try:
            transform = self.tf_buffer.lookup_transform('map', 'base_footprint', rclpy.time.Time())
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = transform.transform.translation.x
            pose.pose.position.y = transform.transform.translation.y
            pose.pose.orientation = transform.transform.rotation
            return pose
        except Exception as e:
            self.get_logger().error(f'Could not get current pose: {e}')
            return None

    def send_next_goal(self):
        if self.current_pose_index < len(self.poses):
            pose = self.poses[self.current_pose_index]
            goal_msg = NavigateToPose.Goal()
            goal_msg.pose = pose

            self.action_client.wait_for_server()
            self._send_goal_future = self.action_client.send_goal_async(goal_msg)
            self._send_goal_future.add_done_callback(self.goal_response_callback)
        else:
            self.get_logger().info('All poses completed')
            rclpy.shutdown()

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return
        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Pose {self.current_pose_index} completed')

        # Update status based on current pose
        if self.current_pose_index < len(self.poses):
            # Check if pose is near inside of any room
            pose = self.poses[self.current_pose_index]
            for room, points in self.room_data.items():
                if 'inside' in points:
                    ins = points['inside']
                    if abs(pose.pose.position.x - ins['x']) < 0.005 and abs(pose.pose.position.y - ins['y']) < 0.005:
                        with open(self.status_file, 'w') as f:
                            f.write(f'in_{room}')
                        self.get_logger().info(f'Status set to in_{room}')
                        break



        self.current_pose_index += 1
        self.send_next_goal()

def create_pose(point):
    return create_pose_with_yaw(point, point['yaw'])

def create_pose_with_yaw(point, yaw_deg):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = point['x']
    pose.pose.position.y = point['y']
    yaw = math.radians(yaw_deg)
    pose.pose.orientation.z = math.sin(yaw / 2)
    pose.pose.orientation.w = math.cos(yaw / 2)
    return pose

def create_wiggle_poses(base_point):
    """Tạo poses wiggle 2 lần: tiến 0.15m, lùi 0.15m, quay trái, quay phải, rồi về gốc, lặp lại để cải thiện localization."""
    poses = []
    base_x = base_point['x']
    base_y = base_point['y']
    base_yaw = base_point['yaw']
    yaw_rad = math.radians(base_yaw)
    
    distance = 0.3
    
    for _ in range(3): 
        # Tiến distance (m)
        forward_x = base_x + distance * math.cos(yaw_rad)
        forward_y = base_y + distance * math.sin(yaw_rad)
        poses.append(create_pose({'x': forward_x, 'y': forward_y, 'yaw': base_yaw}))
        
        # Lùi distance (m)
        backward_x = base_x - distance * math.cos(yaw_rad)
        backward_y = base_y - distance * math.sin(yaw_rad)
        poses.append(create_pose({'x': backward_x, 'y': backward_y, 'yaw': base_yaw}))
        
        # Quay trái 8 độ
        poses.append(create_pose_with_yaw(base_point, base_yaw + 20))
        # Quay phải 8 độ
        poses.append(create_pose_with_yaw(base_point, base_yaw - 20))
        # Quay về gốc
        poses.append(create_pose_with_yaw(base_point, base_yaw))
    return poses

def main(args=None):
    rclpy.init(args=args)
    navigator = RoomNavigator()

    # Get selected rooms from command line, e.g. python room_navigator.py room_101 room_102
    selected_rooms = sys.argv[1:] if len(sys.argv) > 1 else ['room_101']

    # Reset status to 'out'
    status = 'out'
    with open(navigator.status_file, 'w') as f:
        f.write('out')

    # Simplified navigation: go to 'inside' points and perform wiggle
    for i, room in enumerate(selected_rooms):
        if 'inside' in navigator.room_data[room]:
            # Add wiggle before moving to next room (except for first room)
            if i > 0:
                # Get current room's inside point for wiggle
                prev_room = selected_rooms[i-1]
                if 'inside' in navigator.room_data[prev_room]:
                    navigator.poses.extend(create_wiggle_poses(navigator.room_data[prev_room]['inside']))
                    navigator.get_logger().info(f'Added wiggle before moving to {room}')
            
            navigator.poses.append(create_pose(navigator.room_data[room]['inside']))
            navigator.poses.extend(create_wiggle_poses(navigator.room_data[room]['inside']))
            navigator.get_logger().info(f'Added inside point and wiggle for {room}')

    navigator.send_next_goal()
    rclpy.spin(navigator)

if __name__ == '__main__':
    main()