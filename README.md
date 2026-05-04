# Omnidirectional Robot — Nav2 Navigation Stack

This project implements a ROS 2 navigation stack configured for omnidirectional (holonomic) robots. Unlike standard differential-drive setups, this system is designed to take full advantage of lateral movement — eliminating the need to rotate before moving and enabling smoother, more efficient navigation.

The stack integrates localization, global/local planning, costmap management, and behavior-based recovery into a cohesive system optimized for real-world omnidirectional platforms.

## Features

- **Omnidirectional Motion**: Full x/y/theta velocity support — moves laterally without pre-rotation.
- **Optimal Global Planning**: Dijkstra-based path planning on a static occupancy map.
- **Real-time Local Planning**: DWB with 20 Y-axis samples for fine-grained omnidirectional trajectory scoring.
- **Robust Localization**: AMCL with `OmniMotionModel` for accurate pose estimation on holonomic robots.
- **Smart Recovery**: Backup, Wait, and DriveOnHeading behaviors — Spin is intentionally excluded.
- **No-Spin Behavior Trees**: Custom BTs that skip rotation steps unnecessary for omnidirectional platforms.

## System Architecture

The stack consists of the following core components:

- **NavfnPlanner**: Global path planning (Dijkstra algorithm).
- **DWB Local Planner**: Real-time trajectory generation with omnidirectional critic scoring.
- **AMCL**: Particle filter localization using `OmniMotionModel`.
- **Local Costmap**: Rolling 3 m × 3 m window at 5 Hz with VoxelLayer + InflationLayer.
- **Global Costmap**: Static + Obstacle + Inflation layers with unknown space tracking.
- **Behavior Trees**: `navigate_to_pose_no_spin` and `navigate_through_poses_no_spin`.
- **Recovery Behaviors**: Backup, Wait, DriveOnHeading.

## Algorithms & Configuration

| Component | Method / Plugin |
|-----------|----------------|
| Global Planning | NavfnPlanner (Dijkstra, `use_astar: false`) |
| Local Planning | DWB (`dwb_core::DWBLocalPlanner`) |
| Localization | AMCL (`nav2_amcl::OmniMotionModel`) |
| Costmap Obstacle Layer | VoxelLayer (LiDAR) |
| Recovery | Backup → Wait → DriveOnHeading |
| Behavior Trees | No-spin variants (single & multi-pose) |

### DWB Critics (trajectory scoring)

| Critic | Scale |
|--------|-------|
| PathDist | 64.0 |
| RotateToGoal | 60.0 |
| PathAlign | 32.0 |
| GoalDist | 32.0 |
| GoalAlign | 24.0 |
| BaseObstacle | 0.05 |

## Getting Started

```bash
# Source your workspace
source install/setup.bash

# Launch the navigation stack
ros2 launch <your_package> navigation.launch.py

# Send a goal
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{ pose: { header: { frame_id: 'map' }, pose: { position: { x: 1.0, y: 1.0 }, orientation: { w: 1.0 } } } }"
```


