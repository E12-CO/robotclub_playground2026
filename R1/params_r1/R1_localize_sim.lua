include "R1_mapping_sim.lua"

MAP_BUILDER.num_background_threads = 6

-- For localization mode
TRAJECTORY_BUILDER.pure_localization_trimmer = {max_submaps_to_keep = 10,}

POSE_GRAPH.optimize_every_n_nodes = 1 -- Original 1
POSE_GRAPH.constraint_builder.min_score = 0.80  -- Modify 0.55 to 0.65, the minium score of Fast csm, can be optimized above this score 
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.80  -- Modify 0.6 as 0.7, Minimum global positioning score below which global positioning is considered currently inaccurate
POSE_GRAPH.constraint_builder.loop_closure_translation_weight = 100.0
-- POSE_GRAPH.constraint_builder.ceres_scan_matcher.rotation_weight = 1.0
-- POSE_GRAPH.optimization_problem.local_slam_pose_translation_weight = 100

-- For localization mode
-- POSE_GRAPH.constraint_builder.max_constraint_distance = 1.0

POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher.angular_search_window = math.rad(90)
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher.linear_search_window = 0.5

-- Logging
POSE_GRAPH.log_residual_histograms = false
POSE_GRAPH.constraint_builder.log_matches = false
POSE_GRAPH.optimization_problem.log_solver_summary = false

return options
