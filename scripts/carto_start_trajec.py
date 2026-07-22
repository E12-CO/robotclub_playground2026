#!/usr/bin/env python3
# Simple service client node to restart the cartographer trajectory
# Used for Robot retry
# Coded by TinLethax (RB26)
import os

import rclpy
from rclpy.node import Node

import transforms3d
from cartographer_ros_msgs.srv import StartTrajectory, GetTrajectoryStates, FinishTrajectory

from ament_index_python.packages import get_package_share_directory

import sys, select, termios, tty

settings = termios.tcgetattr(sys.stdin)

class carto_start_trajec(Node):
	
	def __init__(self):
		super().__init__('carto_start_trajec')
		self.lastTrajecId = []
		self.KeyFSM = "idle"

		# Create Service clients
		self.GetTrajCli = self.create_client(GetTrajectoryStates, '/r1/get_trajectory_states')
		self.FinTrajCli = self.create_client(FinishTrajectory, '/r1/finish_trajectory')
		self.StartTrajCli = self.create_client(StartTrajectory, '/r1/start_trajectory')

		self.get_logger().info('Starting Carto starter')
		self.timer = self.create_timer(0.05, self.timer_callback)

	def startTrajec(self):
		if not self.StartTrajCli.service_is_ready():
			self.get_logger().info('Waiting for start Trajectory service...')

		self.KeyFSM = 'waitService'

		StartTrajReq = StartTrajectory.Request()
		q = transforms3d.euler.euler2quat(0, 0, 0.0, 'sxyz')
		self.get_logger().info('Sending Start trajectory request to cartographer')
		StartTrajReq.configuration_directory = os.path.join(get_package_share_directory('robotclub_playground2026'), 'R1/params_r1')
		StartTrajReq.configuration_basename = 'R1_localize_sim.lua'
		StartTrajReq.use_initial_pose = True
		StartTrajReq.initial_pose.position.x = 10.0
		StartTrajReq.initial_pose.position.y = 0.0
		StartTrajReq.initial_pose.position.z = 0.0
		StartTrajReq.initial_pose.orientation.x = q[1]
		StartTrajReq.initial_pose.orientation.y = q[2]
		StartTrajReq.initial_pose.orientation.z = q[3]
		StartTrajReq.initial_pose.orientation.w = q[0]
		StartTrajReq.relative_to_trajectory_id = self.lastTrajecId[len(self.lastTrajecId)-1] + 1 # Start on next trajectory ID
		future = self.StartTrajCli.call_async(StartTrajReq)
		future.add_done_callback(self.startTrajecCallback)

	def startTrajecCallback(self, future):
		try:
			startTrajRes = future.result()
			self.get_logger().info(
				f'Started new trajectory'
			)
		except Exception as e:
			self.get_logger().error(f'Service call failed {e}')

		self.KeyFSM = 'idle'

	def getTrajecId(self):
		if not self.GetTrajCli.service_is_ready():
			self.get_logger().info('Waiting for Trajectory ID service...')
			return

		self.KeyFSM = 'waitService'

		self.get_logger().info('Request Current Trajectory ID')
		GetTrajReq = GetTrajectoryStates.Request()
		future = self.GetTrajCli.call_async(GetTrajReq)
		future.add_done_callback(self.getTrajecIdCallback)

	def getTrajecIdCallback(self, future):
		try:
			trajIdRes = future.result()
			self.lastTrajecId = trajIdRes.trajectory_states.trajectory_id[:-1]
			self.get_logger().info(f'Latest trajectory ID : {self.lastTrajecId}')
			self.KeyFSM = "gotId"
		except Exception as e:
			self.get_logger().error(f'Service call failed {e}')
			self.KeyFSM = 'idle'

	def finishTraj(self, tId):
		if not self.FinTrajCli.service_is_ready():
			self.get_logger().info('Waiting for Finish Trajectory service...')
			return

		self.KeyFSM = 'waitService'

		self.get_logger().info('Finishing current trajectory')
		FinTrajReq = FinishTrajectory.Request()
		FinTrajReq.trajectory_id = tId[len(tId)-1]

		future = self.FinTrajCli.call_async(FinTrajReq)
		future.add_done_callback(self.finishTrajCallback)

	def finishTrajCallback(self, future):
		try:
			finTrajRes = future.result()
			self.get_logger().info('Finished current trajectory')
			self.KeyFSM = 'finished'
		except Exception as e:
			self.get_logger().error(f'Service call failed {e}')

	def timer_callback(self):
		match self.KeyFSM:
			case 'idle':
				key = getKey()
				if key == 'r': # if press 'r', restart cartographer
					self.KeyFSM = 'waitId'
				elif key == 'c':
					rclpy.shutdown()

			case 'waitId':
				# Get current trajectory
				self.getTrajecId()
				return

			case 'gotId':
				# Finish the current trajectory
				self.finishTraj(self.lastTrajecId)

			case 'finished':
				# Restart the cartographer with next trajectory Id
				self.startTrajec()
				

			case 'waitService':
				return
	
			case _:
				self.KeyFSM = 'idle'

def getKey():
	tty.setraw(sys.stdin.fileno())
	key = ''
	if select.select([sys.stdin], [], [], 0.05) == ([sys.stdin], [], []):
		key = sys.stdin.read(1)
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
	return key

def main(args=None):
	rclpy.init(args=args)

	carto_client = carto_start_trajec()
	rclpy.spin(carto_client)
	rclpy.shutdown()

if __name__ == '__main__':
	main()
