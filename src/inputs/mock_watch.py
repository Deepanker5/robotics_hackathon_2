"""
Mock watch input source for testing without real hardware.
"""

import time
import random
from typing import Optional
from src.inputs.watch_input import WatchInputSource, WatchOrientation, WatchGesture


class MockWatchInput(WatchInputSource):
    """Mock watch input that simulates watch data for local testing."""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize mock watch input.
        
        Args:
            verbose: Whether to print debug info
        """
        self._connected = False
        self._verbose = verbose
        self._orientation = WatchOrientation(roll=0.0, pitch=0.0)
        self._last_gesture_time = 0
        self._gesture_queue: list = []
        self._last_poll_time = time.time()
    
    def connect(self) -> bool:
        """Simulate connecting to watch."""
        self._connected = True
        if self._verbose:
            print("[MockWatch] Connected")
        return True
    
    def disconnect(self) -> None:
        """Simulate disconnecting from watch."""
        self._connected = False
        if self._verbose:
            print("[MockWatch] Disconnected")
    
    def is_connected(self) -> bool:
        """Check if mock is in connected state."""
        return self._connected
    
    def get_orientation(self) -> Optional[WatchOrientation]:
        """Get the current orientation."""
        if not self._connected:
            return None
        return self._orientation
    
    def get_gesture(self) -> Optional[WatchGesture]:
        """Get and remove the next gesture from the queue."""
        if not self._connected or not self._gesture_queue:
            return None
        return self._gesture_queue.pop(0)
    
    def poll(self) -> None:
        """
        Poll for new data. Simulates orientation updates.
        """
        if not self._connected:
            return
        
        current_time = time.time()
        elapsed = current_time - self._last_poll_time
        self._last_poll_time = current_time
        
        # Simulate slow random orientation drift
        self._orientation.roll += random.uniform(-2.0, 2.0)
        self._orientation.pitch += random.uniform(-2.0, 2.0)
        
        # Clamp to reasonable range
        self._orientation.roll = max(-90, min(90, self._orientation.roll))
        self._orientation.pitch = max(-90, min(90, self._orientation.pitch))
    
    def inject_orientation(self, roll: float, pitch: float) -> None:
        """
        Inject a specific orientation for testing.
        
        Args:
            roll: Roll angle in degrees
            pitch: Pitch angle in degrees
        """
        self._orientation = WatchOrientation(roll=roll, pitch=pitch)
    
    def inject_gesture(self, gesture_type: str) -> None:
        """
        Inject a gesture event for testing.
        
        Args:
            gesture_type: Type of gesture (e.g., "tap")
        """
        gesture = WatchGesture(
            gesture_type=gesture_type,
            timestamp_ms=int(time.time() * 1000)
        )
        self._gesture_queue.append(gesture)
        if self._verbose:
            print(f"[MockWatch] Gesture injected: {gesture_type}")
