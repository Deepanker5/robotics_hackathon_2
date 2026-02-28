"""
Watch input interfaces and implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class WatchOrientation:
    """
    Represents the current orientation of the watch.
    
    Angles are in degrees:
    - roll: rotation around the long axis of the arm (left-right tilt)
    - pitch: forward-backward tilt
    """
    
    roll: float
    pitch: float


@dataclass
class WatchGesture:
    """Represents a detected gesture on the watch."""
    
    gesture_type: str
    timestamp_ms: int


class WatchInputSource(ABC):
    """Abstract base class for watch input sources."""
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the watch device.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the watch device."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if currently connected to the watch."""
        pass
    
    @abstractmethod
    def get_orientation(self) -> Optional[WatchOrientation]:
        """
        Get the current watch orientation.
        
        Returns:
            WatchOrientation if available, None if disconnected or no data
        """
        pass
    
    @abstractmethod
    def get_gesture(self) -> Optional[WatchGesture]:
        """
        Get the latest gesture event (if any).
        
        Returns:
            WatchGesture if a gesture occurred, None otherwise
        """
        pass
    
    @abstractmethod
    def poll(self) -> None:
        """
        Poll the watch for new data.
        
        Call this regularly to update internal state.
        May raise exceptions if connection is lost.
        """
        pass
