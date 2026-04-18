#!/usr/bin/env python3
import sys
import os

status_file = '/home/huylake/ros2_ws/src/omni_based_robot/omni_base_bringup/config/nav2/status.txt'

if len(sys.argv) > 1:
    status = sys.argv[1]
    with open(status_file, 'w') as f:
        f.write(status)
    print(f'Status set to {status}')
else:
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            print(f'Current status: {f.read().strip()}')
    else:
        print('Status file not found')