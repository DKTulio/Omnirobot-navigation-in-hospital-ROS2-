import rclpy
from rclpy.node import Node
import math
from geometry_msgs.msg import Twist, TwistStamped
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu

def euler_from_quaternion(quaternion):
    x = quaternion.x
    y = quaternion.y
    z = quaternion.z
    w = quaternion.w
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)

def quaternion_from_euler(yaw):
    w = math.cos(yaw / 2.0)
    x = 0.0
    y = 0.0
    z = math.sin(yaw / 2.0)
    return [x, y, z, w]

class TwistStamper(Node):
    def __init__(self):
        super().__init__('twist_stamper')
        self.sub = self.create_subscription(Twist, '/mobile_base_controller/cmd_vel_unstamped', self.listener_callback, 10)
        self.pub = self.create_publisher(TwistStamped, '/mobile_base_controller/reference', 10)

        # Relay cho tf, odometry và chèn dữ liệu góc quay từ IMU để diệt trượt bánh
        self.tf_sub = self.create_subscription(TFMessage, '/mobile_base_controller/tf_odometry', self.tf_callback, 50)
        self.tf_pub = self.create_publisher(TFMessage, '/tf', 50)
        
        self.odom_sub = self.create_subscription(Odometry, '/mobile_base_controller/odometry', self.odom_callback, 50)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 50)

        self.imu_sub = self.create_subscription(Imu, '/base_imu', self.imu_callback, 50)
        
        self.imu_yaw = None
        self.imu_yaw_offset = None

    def imu_callback(self, msg):
        self.imu_yaw = euler_from_quaternion(msg.orientation)

    def listener_callback(self, msg):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = 'base_footprint'
        stamped.twist = msg
        self.pub.publish(stamped)

    def apply_imu_to_quat(self, quat):
        if self.imu_yaw is not None:
            if self.imu_yaw_offset is None:
                # Lưu lại góc ban đầu để căn bằng với odom (odom luôn xuất phát = 0)
                self.imu_yaw_offset = self.imu_yaw
            
            # Góc thật của xe bằng góc hiện tại của IMU trừ đi góc lúc spawn
            real_yaw = self.imu_yaw - self.imu_yaw_offset
            q = quaternion_from_euler(real_yaw)
            quat.x = q[0]
            quat.y = q[1]
            quat.z = q[2]
            quat.w = q[3]

    def tf_callback(self, msg):
        for transform in msg.transforms:
            if transform.child_frame_id == 'base_footprint' and transform.header.frame_id == 'odom':
                self.apply_imu_to_quat(transform.transform.rotation)
        self.tf_pub.publish(msg)

    def odom_callback(self, msg):
        self.apply_imu_to_quat(msg.pose.pose.orientation)
        self.odom_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(TwistStamper())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
