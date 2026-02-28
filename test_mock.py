#!/usr/bin/env python3
"""
Test script for manual control system.
Runs the system for a brief period and demonstrates functionality.
"""

import sys
import os
import time
import threading

# Add project root to path
sys.path.insert(0, '/Users/deepanker/Desktop/robotics_hackathon_2')

from src.main import create_app


def test_mock_mode():
    """Test the mock mode briefly."""
    print("\n" + "="*70)
    print("Testing Manual Control System - Mock Mode")
    print("="*70 + "\n")
    
    try:
        # Create app in mock mode with verbose logging
        controller, logger = create_app(mock_mode=True, verbose=True)
        
        # Simulate watch input
        logger.info("test", "Injecting simulated watch data...")
        watch = controller.watch_input
        
        # Connect the watch first
        if not watch.connect():
            raise RuntimeError("Failed to connect mock watch")
        logger.info("test", "Mock watch connected")
        
        # Inject orientation to trigger commands
        print("\n--- Simulating forward tilt ---")
        watch.inject_orientation(roll=0, pitch=30)
        controller._process_watch_data()
        
        print("\n--- Simulating left tilt ---")
        watch.inject_orientation(roll=-30, pitch=0)
        controller._process_watch_data()
        
        print("\n--- Simulating stop (neutral) ---")
        watch.inject_orientation(roll=0, pitch=0)
        controller._process_watch_data()
        
        print("\n--- Simulating gesture tap ---")
        watch.inject_gesture("tap")
        controller._process_watch_data()
        
        print("\n" + "="*70)
        print("✓ Test completed successfully!")
        print("="*70 + "\n")
        
        return True
    
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_mock_mode()
    sys.exit(0 if success else 1)
