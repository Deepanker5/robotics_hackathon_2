"""
Inputs module - exports input sources.
"""

from src.inputs.watch_input import WatchInputSource, WatchOrientation, WatchGesture
from src.inputs.mock_watch import MockWatchInput

__all__ = [
    "WatchInputSource",
    "WatchOrientation",
    "WatchGesture",
    "MockWatchInput",
]
