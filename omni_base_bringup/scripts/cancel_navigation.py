#!/usr/bin/env python3
import subprocess
import sys

def cancel_navigation():
    try:
        # Cancel NavigateThroughPoses action (used by room_navigator)
        result1 = subprocess.run(['ros2', 'action', 'cancel', '/navigate_through_poses'], capture_output=True, text=True)
        print("Cancel NavigateThroughPoses:", result1.stdout or result1.stderr)
        
        # Also cancel NavigateToPose in case
        result2 = subprocess.run(['ros2', 'action', 'cancel', '/navigate_to_pose'], capture_output=True, text=True)
        print("Cancel NavigateToPose:", result2.stdout or result2.stderr)
        
        print("Navigation canceled!")
    except Exception as e:
        print(f"Error canceling navigation: {e}")

if __name__ == '__main__':
    cancel_navigation()