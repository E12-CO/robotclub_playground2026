# Trajectory smoother with save to CSV capabilities
# Thanks god ChatGPT can help me write python

import csv
import math
import sys

import transforms3d
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Pose
from nav_msgs.msg import Path

import numpy as np
from ccma import CCMA

import os, sys, select, termios, tty

settings = termios.tcgetattr(sys.stdin)

class PathInterpolator(Node):
    def __init__(self, filename):
        super().__init__('path_interpolator', namespace='r1')
        self.linearPreviewPub_  = self.create_publisher(Path, 'interpolated_path', 10)
        self.smoothPreviewPub_  = self.create_publisher(Path, 'smooth_path', 10)
        self.smoothPathPub_     = self.create_publisher(Path, 'path', 10) 
        self.subscription_ = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.pose_callback,
            10
        )
        
        self.poseArray = []
        self.linearPath_msg = Path()
        self.smoothPath_msg = Path()
        self.linearPath_msg.header.frame_id = 'map'
        self.ccma = CCMA(w_ma=300, w_cc=3)

        self.pathCSVName = filename
#        with open(self.pathCSVName, mode='w', newline='\n') as file:
#            writer = csv.writer(file)
#            writer.writerow(['X', 'Y', 'Yaw'])

        self.last_point = None
        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info("Robot Club Engineering KMITL : starting Path Interpolator...")

    def quat_to_yaw(self, x, y, z, w):
        (row, pitch, yaw) = transforms3d.euler.quat2euler([w, x, y, z], 'sxyz')
        return yaw

    def interpolate_points(self, start, end, num_points):
        x_values = np.linspace(start[0], end[0], num_points + 2)
        y_values = np.linspace(start[1], end[1], num_points + 2)
        yaw_values = np.linspace(start[2], end[2], num_points + 2)
        return [(x, y, yaw) for x, y, yaw in zip(x_values, y_values, yaw_values)]


    def pose_callback(self, msg):
        """
        Callback function for processing incoming PoseStamped messages.
        """
        self.get_logger().info('Received Pose')
        self.poseArray.append(msg)
        self.pose_interpolatePoints()

    def pose_interpolatePoints(self):
        if len(self.poseArray) < 2:
            self.linearPath_msg.poses.clear()
            self.linearPath_msg.header.stamp = self.get_clock().now().to_msg()
            self.linearPreviewPub_.publish(self.linearPath_msg)
            return
    
        # Clear previous poses
        self.linearPath_msg.poses.clear()
    
        for i in range(len(self.poseArray) - 1):
            current_point = (
                self.poseArray[i].pose.position.x, 
                self.poseArray[i].pose.position.y,
                self.quat_to_yaw(
                    self.poseArray[i].pose.orientation.x,
                    self.poseArray[i].pose.orientation.y,
                    self.poseArray[i].pose.orientation.z,
                    self.poseArray[i].pose.orientation.w
                )
                )
        
            next_point = (
                self.poseArray[i+1].pose.position.x, 
                self.poseArray[i+1].pose.position.y,
                self.quat_to_yaw(
                    self.poseArray[i+1].pose.orientation.x,
                    self.poseArray[i+1].pose.orientation.y,
                    self.poseArray[i+1].pose.orientation.z,
                    self.poseArray[i+1].pose.orientation.w
                )
                )
        
            interpolated_points = self.interpolate_points(current_point, next_point, num_points=50)

            for lPose in interpolated_points:
                pose = PoseStamped()
                pose.header.frame_id = 'map'
                pose.header.stamp = self.get_clock().now().to_msg()
                pose.pose.position.x = lPose[0]
                pose.pose.position.y = lPose[1]
                pose.pose.position.z = 0.0
                q = transforms3d.euler.euler2quat(0, 0, lPose[2], 'sxyz')
                pose.pose.orientation.x = q[1]
                pose.pose.orientation.y = q[2]
                pose.pose.orientation.z = q[3]
                pose.pose.orientation.w = q[0]
                self.linearPath_msg.poses.append(pose)

            print("Interpolated path length:", len(self.linearPath_msg.poses))

        # Publish the linear interpolated path
        self.linearPath_msg.header.stamp = self.get_clock().now().to_msg()
        self.linearPreviewPub_.publish(self.linearPath_msg)
    
        # Update the smooth path
        self.pose_generateSmoothPath()
    
    def pose_generateSmoothPath(self):
        x_list = []
        y_list = []
        for xy_point in self.linearPath_msg.poses:
            x_list.append(xy_point.pose.position.x)
            y_list.append(xy_point.pose.position.y)

        smooth_path = self.ccma.filter(np.column_stack([x_list,y_list]), cc_mode=False)
        
        self.smoothPath_msg.poses.clear() # Clear all previous path before regenerating them
        self.smoothPath_msg.header.frame_id = 'map'
        
        # Insert initial point
        smoothPose = PoseStamped()
        smoothPose.header.frame_id = 'map'
        smoothPose.header.stamp = self.get_clock().now().to_msg()
        smoothPose.pose.position.x = self.linearPath_msg.poses[0].pose.position.x
        smoothPose.pose.position.y = self.linearPath_msg.poses[0].pose.position.y
        self.smoothPath_msg.poses.append(smoothPose)

        for smooth_pose in smooth_path:
            smoothPose = PoseStamped()
            smoothPose.header.frame_id = 'map'
            smoothPose.header.stamp = self.get_clock().now().to_msg()
            smoothPose.pose.position.x = smooth_pose[0]
            smoothPose.pose.position.y = smooth_pose[1]
            self.smoothPath_msg.poses.append(smoothPose)

        # Insert last point
        smoothPose.header.stamp = self.get_clock().now().to_msg()
        smoothPose.pose.position.x = self.linearPath_msg.poses[-1].pose.position.x
        smoothPose.pose.position.y = self.linearPath_msg.poses[-1].pose.position.y
        self.smoothPath_msg.poses.append(smoothPose)

        # Copy YAW
        self.smoothPath_msg.poses[0].pose.orientation = self.linearPath_msg.poses[0].pose.orientation

        for yaw_pose_idx in range(0, len(self.linearPath_msg.poses)):
            self.smoothPath_msg.poses[yaw_pose_idx+1].pose.orientation = self.linearPath_msg.poses[yaw_pose_idx].pose.orientation

        self.smoothPath_msg.poses[-1].pose.orientation = self.linearPath_msg.poses[-1].pose.orientation

        print("Smooth path length:", len(self.smoothPath_msg.poses))

        # Update the Path header timestamp
        self.smoothPath_msg.header.stamp = self.get_clock().now().to_msg()
        # Publish the updated Path
        self.smoothPreviewPub_.publish(self.smoothPath_msg)

    def timer_callback(self):
        # Keypress detection
        Key = getKey()
        
        if Key == 'r':
            # Clear current path
            self.get_logger().info("Clear current Path...")
            self.linearPath_msg.poses.clear()
            self.last_point = None
        if Key == 'z':
            # Undo last point
            if len(self.poseArray) > 0:
                self.get_logger().info("Undoing last point")
                self.poseArray.pop()
                self.pose_interpolatePoints() # Update the path
                
        elif Key == 's':
            if len(self.linearPath_msg.poses) < 2:
                return

            # Smoothing the path
            self.get_logger().info('Publishing smooth Path...')
            self.smoothPathPub_.publish(self.smoothPath_msg)

def getKey():
    tty.setcbreak(sys.stdin.fileno())
    key = ''
    if select.select([sys.stdin], [], [], 0.05) == ([sys.stdin], [], []):
        key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main(args=None):
    rclpy.init(args=args)

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print('Error! Please provice the save file name')
        exit()

    node = PathInterpolator(filename)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

