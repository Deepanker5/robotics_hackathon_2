"""
Command definitions for the manual control system.
"""

from enum import Enum, auto


class MotionCommand(Enum):
    """Motion commands that can be sent to the robot."""
    
    MOVE_FORWARD = auto()
    MOVE_BACKWARD = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    STOP = auto()


class ActionCommand(Enum):
    """Action commands (non-motion)."""
    
    PICKUP = auto()


class RobotCommand:
    """
    Represents a complete command to the robot.
    
    A command can be either a motion command or an action command.
    """
    
    def __init__(self, motion: 'MotionCommand | None' = None, action: 'ActionCommand | None' = None):
        """
        Initialize a robot command.
        
        Args:
            motion: Motion command, or None if only action
            action: Action command, or None if only motion
        """
        if motion is None and action is None:
            raise ValueError("At least one of motion or action must be provided")
        
        self.motion = motion
        self.action = action
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RobotCommand):
            return NotImplemented
        return self.motion == other.motion and self.action == other.action
    
    def __repr__(self) -> str:
        parts = []
        if self.motion:
            parts.append(f"motion={self.motion.name}")
        if self.action:
            parts.append(f"action={self.action.name}")
        return f"RobotCommand({', '.join(parts)})"
    
    def is_motion_only(self) -> bool:
        """Check if this is a motion-only command."""
        return self.motion is not None and self.action is None
    
    def is_action_only(self) -> bool:
        """Check if this is an action-only command."""
        return self.motion is None and self.action is not None
    
    def is_motion_stop(self) -> bool:
        """Check if this is a stop command."""
        return self.motion == MotionCommand.STOP
