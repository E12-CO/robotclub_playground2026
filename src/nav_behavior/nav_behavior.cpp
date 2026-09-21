#include "nav_behavior.hpp"

// XML to load the navigation behavior
const std::string bt_xml_dir =
    ament_index_cpp::get_package_share_directory("robotclub_playground2026") + "/behavior";

NavAction::NavAction(
	const std::string &name,
	const BT::NodeConfiguration &config,
	std::shared_ptr<NavBehaviorNode> node
	) :
	BT::StatefulActionNode(name, config),
	node_instant_(node){
	
	RCLCPP_INFO(
		node_instant_->get_logger(),
		"Instantiating the NavBehavior actions..."
	);
	
		
}

// onStart() send the file name of navigation paths to irob_trajectory_maker node
BT::NodeStatus NavAction::onStart(){
	RCLCPP_INFO(
		node_instant_->get_logger(),
		"Starting NavAction"
	);
	
	geometry_msgs::msg::PoseStamped		tempPose;
	
	tempPose.header.frame_id = "map";
	tempPose.header.stamp =  node_instant_->get_clock()->now();
	
	tempPose.pose.position.x = 2.0;
	tempPose.pose.position.y = 2.0;
	node_instant_->pubPathMessage.poses.push_back(tempPose);
	
	tempPose.pose.position.x = 4.0;
	tempPose.pose.position.y = 2.0;
	node_instant_->pubPathMessage.poses.push_back(tempPose);
	
	tempPose.pose.position.x = 6.0;
	tempPose.pose.position.y = 2.0;
	node_instant_->pubPathMessage.poses.push_back(tempPose);
	
	RCLCPP_INFO(
		node_instant_->get_logger(),
		"Publishing goal pose with %d points",
		node_instant_->pubPathMessage.poses.size()
	);
	
	node_instant_->pubPathMessage.header.stamp = tempPose.header.stamp;
	node_instant_->pubPath->publish(node_instant_->pubPathMessage);
	
	return BT::NodeStatus::RUNNING;
}

BT::NodeStatus NavAction::onRunning(){

	if(node_instant_->sIrobStatMsg == "done"){
		// received status message with "done"
		return BT::NodeStatus::SUCCESS;
		
	}else if(node_instant_->sIrobStatMsg == "failed"){
		// navigation failure
		RCLCPP_ERROR(
			node_instant_->get_logger(),
			"iRob maneuv3r tracker failed to lookup transform!"
		);
		
		return BT::NodeStatus::FAILURE;
		
	}else if(node_instant_->sIrobStatMsg == "canceled"){
		// goal canceled
		RCLCPP_INFO(
			node_instant_->get_logger(),
			"Goal canceled!"
		);
		
		return BT::NodeStatus::FAILURE;
		
	}
	
	return BT::NodeStatus::RUNNING;
}

void NavAction::onHalted(){
	RCLCPP_ERROR(
		node_instant_->get_logger(),
		"NavAction halted!"
	);
	
	node_instant_->irobCmd.irobcmd = "stop";
	
	node_instant_->pubIrobCmd->publish(node_instant_->irobCmd);
}

/*
*
* Nav behavior node code
*
*/

NavBehaviorNode::NavBehaviorNode() : Node("nav_behavior"){
	
	
};

void NavBehaviorNode::nav_setup(){
	RCLCPP_INFO(
		this->get_logger(),
		"Robot Club Engineering KMITL : Starting navigation behavior node..."
	);
	
	NavBehaviorNode::nav_createBehaviorTree();
	
	// Path publisher
	pubPath = create_publisher<nav_msgs::msg::Path>("poses", 10);
	// Setup the path message header
	pubPathMessage.header.frame_id = "map";
	
	// irob cmd publisher
	pubIrobCmd = create_publisher<irob_msgs::msg::IrobCmdMsg>("irob_cmd", 10);
	
	// irob maneuv3r status subscription
	subIrobStat = 
		create_subscription<irob_msgs::msg::IrobCmdMsg>(
		"irob_stat",
		10,
		std::bind(
			&NavBehaviorNode::nav_irobManeuv3rStatCallback,
			this,
			std::placeholders::_1)
		);
	
	timer = 
			this->create_wall_timer(
				std::chrono::milliseconds(10),
				std::bind(
					&NavBehaviorNode::nav_treeTick, 
					this)
			);
	
	rclcpp::spin(shared_from_this());
	rclcpp::shutdown();

}

void NavBehaviorNode::nav_irobManeuv3rStatCallback(const irob_msgs::msg::IrobCmdMsg::SharedPtr irob_stat){
	// Copy the irob status sting.
	sIrobStatMsg = irob_stat->irobcmd;
}

void NavBehaviorNode::nav_createBehaviorTree(){
	BT::BehaviorTreeFactory btFactory;
	
	RCLCPP_INFO(
		this->get_logger(),
		"Registering actions and creating tree..."
	);
	
	BT::NodeBuilder builder =
      [=](const std::string &name, const BT::NodeConfiguration &config)
	  {
		return std::make_unique<NavAction>(
			name, 
			config, 
			std::static_pointer_cast<NavBehaviorNode>(shared_from_this())
		);
	  };

	btFactory.registerBuilder<NavAction>("NavAction", builder);
	
	RCLCPP_INFO(
		this->get_logger(),
		"behavior xml folder %s",
		bt_xml_dir.c_str()
	);
	
	nav_tree_ = btFactory.createTreeFromFile(bt_xml_dir + "/nav_behavior.xml");
}

void NavBehaviorNode::nav_treeTick(){
	BT::NodeStatus tree_status = nav_tree_.tickRoot();

	if (tree_status == BT::NodeStatus::RUNNING){
		return;
	}else if (tree_status == BT::NodeStatus::SUCCESS){
		RCLCPP_INFO(
			this->get_logger(), 
			"Finished Navigation"
		);
		timer->cancel();
	}else if (tree_status == BT::NodeStatus::FAILURE){
		RCLCPP_INFO(
			this->get_logger(), 
			"Navigation Failed"
		);
		timer->cancel();
	}
	
}

int main(int argc, char **argv){
	rclcpp::init(argc, argv);
	auto navBhvr = std::make_shared<NavBehaviorNode>();
	navBhvr->nav_setup();
	
}