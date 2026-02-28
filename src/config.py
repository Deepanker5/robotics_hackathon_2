"""
Configuration and constants for the manual control subsystem.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WatchInputConfig:
    """Configuration for watch input interpretation."""
    
    # Orientation thresholds (in degrees) for detecting movement
    # If wrist tilt magnitude is below this, consider it neutral
    dead_zone_threshold: float = 10.0
    
    # Threshold for detecting significant orientation change
    orientation_change_threshold: float = 5.0
    
    # Debounce time for gesture recognition (milliseconds)
    gesture_debounce_ms: int = 200
    
    # Connection timeout (seconds)
    connection_timeout_s: float = 5.0


@dataclass
class RobotConfig:
    """Configuration for robot behavior."""
    
    # Maximum velocity (0-100, represented as percentage)
    max_velocity: int = 100
    
    # Acceleration ramp time (milliseconds)
    ramp_time_ms: int = 100


@dataclass
class AppConfig:
    """Main application configuration."""
    
    watch_input: WatchInputConfig
    robot: RobotConfig
    
    # Enable mock/dry-run mode (no real hardware)
    mock_mode: bool = True
    
    # Verbose logging
    verbose: bool = False
    
    # Heartbeat log interval in seconds (0 to disable)
    heartbeat_interval_s: float = 0.0


def get_default_config(mock_mode: bool = True, verbose: bool = False) -> AppConfig:
    """
    Get the default application configuration.
    
    Args:
        mock_mode: Whether to run in mock/dry-run mode
        verbose: Whether to enable verbose logging
    
    Returns:
        AppConfig with sensible defaults
    """
    return AppConfig(
        watch_input=WatchInputConfig(),
        robot=RobotConfig(),
        mock_mode=mock_mode,
        verbose=verbose,
        heartbeat_interval_s=5.0 if verbose else 0.0,
    )
