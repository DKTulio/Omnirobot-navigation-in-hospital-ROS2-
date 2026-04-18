#!/usr/bin/env python3
# ROS 2 Node wrapper for twist_stamper functionality

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped

class TwistStamperNode(Node):
    def __init__(self):
        super().__init__('twist_stamper')
        
        self.sub = self.create_subscription(Twist, '/mobile_base_controller/cmd_vel_unstamped', self.listener_callback, 10)
        self.pub = self.create_publisher(TwistStamped, '/mobile_base_controller/reference', 10)
        
        self.get_logger().info('TwistStamper node started. Relaying twist messages.')

    def listener_callback(self, msg):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = 'base_footprint'
        stamped.twist = msg
        self.pub.publish(stamped)

def main(args=None):
    rclpy.init(args=args)
    node = TwistStamperNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
