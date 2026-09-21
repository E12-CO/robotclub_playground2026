#ifndef NAV_BEHAVIOR_HPP
#define HAV_BEHAVIOR_HPP

// ROS2 libraries
#include <rclcpp/rclcpp.hpp>

// Nav msgs
#include <nav_msgs/msg/path.hpp>

// Geometry msgs
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/pose.hpp>

// iRob command message
#include "irob_msgs/msg/irob_cmd_msg.hpp"

// Behavior tree library
#include "behaviortree_cpp_v3/behavior_tree.h"
#include "behaviortree_cpp_v3/bt_factory.h"

// Helper 
#include "ament_index_cpp/get_package_share_directory.hpp"

class NavBehaviorNode : public rclcpp::Node {
	public :
	
	// subscription to irob_maneuv3r on irob_stat message
	rclcpp::Subscription<irob_msgs::msg::IrobCmdMsg>::SharedPtr subIrobStat;
	std::string sIrobStatMsg;
	
	// irob_maneuv3r control message
	rclcpp::Publisher<irob_msgs::msg::IrobCmdMsg>::SharedPtr pubIrobCmd;
	irob_msgs::msg::IrobCmdMsg	irobCmd;
	
	// Path publisher
	rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr		pubPath;
	
	nav_msgs::msg::Path pubPathMessage;
	
	// Wall timer to tick the tree
	rclcpp::TimerBase::SharedPtr timer;
	
	explicit NavBehaviorNode();
	
	void nav_setup();
	
	void nav_irobManeuv3rStatCallback(const irob_msgs::msg::IrobCmdMsg::SharedPtr irob_stat);
	
	void nav_createBehaviorTree();
	
	void nav_treeTick();
	
	private:
	BT::Tree nav_tree_;
	
};

// Navigation Action. Asynchronous behavior type (StatefulActionNode).
class NavAction : public BT::StatefulActionNode{
	public:
	
	NavAction(
		const std::string &name,
        const BT::NodeConfiguration &config,
		std::shared_ptr<NavBehaviorNode> node
	);
	
	// static BT::PortsList providedPorts()
	// {
		// return {};
	// }
	
	BT::NodeStatus 	onStart() override;
	BT::NodeStatus 	onRunning() override;
	void			onHalted() override;
	
	std::string		nav_status;
	std::shared_ptr<NavBehaviorNode> node_instant_;
	
	int i32NavCount;
};

#endif