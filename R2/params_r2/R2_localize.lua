include "map_builder.lua"  
include "trajectory_builder.lua"  

options = {
  map_builder = MAP_BUILDER,  
  trajectory_builder = TRAJECTORY_BUILDER,  
  map_frame = "map",  -- map frame name 
  tracking_frame = "base_link_r2",  -- tracking frame name
  published_frame = "base_link_r2",  -- published frame name 
  odom_frame = "odom_r1",  -- name of the odometer frame
  provide_odom_frame = false,  -- whether to provide the odometer frame
  publish_frame_projected_to_2d = true,  -- whether to publish 2d gesture  
  use_pose_extrapolator = false,
  use_odometry = false,  -- whether use odometry
  use_nav_sat = false,  -- whether use the navigation satellite 
  use_landmarks = false,  -- whether use the landmark
  num_laser_scans = 2,  -- LiDAR number  
  num_multi_echo_laser_scans = 0,  -- number of multi-echo LiDAR  
  num_subdivisions_per_laser_scan = 1,  -- number of subdivisions for each laser scan
  num_point_clouds = 0,  -- number of cloud points
  lookup_transform_timeout_sec = 0.5,  -- timeout for finding transformations (seconds)  
  submap_publish_period_sec = 0.3,  -- submap release cycle (seconds)
  pose_publish_period_sec = 5e-2,  -- attitude release period (seconds)
  publish_tracked_pose = true, -- publish tracked pose (trajectory server)
  trajectory_publish_period_sec = 40e-3,  -- trajectory release period (seconds)
  rangefinder_sampling_ratio = 1.0,  -- rangefinder sampling ratio
  odometry_sampling_ratio = 1.0,  -- odometer sampling rate
  fixed_frame_pose_sampling_ratio = 1.,  -- fixed frame attitude sampling ratio  
  imu_sampling_ratio = 1.,  -- IMU sampling ratio
  landmarks_sampling_ratio = 1.,  -- landmarks sampling ratio
}
 
MAP_BUILDER.use_trajectory_builder_2d = true  -- whether use 2D SLAM
TRAJECTORY_BUILDER_2D.num_accumulated_range_data = 4 -- Accumulate two hokuyo scan data 
TRAJECTORY_BUILDER_2D.submaps.num_range_data = 20  -- Max is 100
TRAJECTORY_BUILDER_2D.min_range = 0.1  -- ignore anything smaller than the robot radius, limiting it to the minimum scan range of the lidar
TRAJECTORY_BUILDER_2D.max_range = 11.0  -- the maximum scanning range of the lidar
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 8.0  -- Restricted to maximum LiDAR scanning range  
TRAJECTORY_BUILDER_2D.voxel_filter_size = 0.05
TRAJECTORY_BUILDER_2D.use_imu_data = false  -- whether use IMU data

TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true  -- Whether to scan for matches using real-time loopback detection
-- TRAJECTORY_BUILDER_2D.real_time_correlative_scan_matcher.linear_search_window = 0.2 -- Default 0.1

-- TRAJECTORY_BUILDER_2D.ceres_scan_matcher.occupied_space_weight = 1.
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.translation_weight = 0.8
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.rotation_weight = 2
TRAJECTORY_BUILDER_2D.ceres_scan_matcher.ceres_solver_options.max_num_iterations = 1000

TRAJECTORY_BUILDER_2D.motion_filter.max_time_seconds = 0.1
TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = math.rad(1.0)  -- Modify to 1 degree
TRAJECTORY_BUILDER_2D.motion_filter.max_distance_meters = 0.15

-- For localization mode
TRAJECTORY_BUILDER.pure_localization_trimmer = {max_submaps_to_keep = 3,}

POSE_GRAPH.optimize_every_n_nodes = 1 -- Original 1
POSE_GRAPH.constraint_builder.min_score = 0.80  -- Modify 0.55 to 0.65, the minium score of Fast csm, can be optimized above this score 
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.80  -- Modify 0.6 as 0.7, Minimum global positioning score below which global positioning is considered currently inaccurate

-- For localization mode
-- POSE_GRAPH.constraint_builder.max_constraint_distance = 4.5
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher.angular_search_window = math.rad(180)
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher.linear_search_window = 1.0
return options
