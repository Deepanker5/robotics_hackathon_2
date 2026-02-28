"""
Interpreter layer: converts raw watch data into semantic commands.
"""

from src.config import WatchInputConfig
from src.inputs.watch_input import WatchOrientation, WatchGesture
from src.utils.commands import MotionCommand, ActionCommand
from src.utils.logger import Logger


class WatchInterpreter:
    """
    Converts watch orientation and gestures into motion and action commands.
    """
    
    def __init__(self, config: WatchInputConfig, logger: Logger):
        """
        Initialize the interpreter.
        
        Args:
            config: Watch input configuration with thresholds
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self._last_motion_command: 'MotionCommand | None' = None
        self._last_gesture_time: int = 0
    
    def interpret_orientation(self, orientation: WatchOrientation) -> 'MotionCommand | None':
        """
        Interpret watch orientation into a motion command.
        
        Implements dead zone logic to avoid noise.
        
        Args:
            orientation: Current watch orientation
        
        Returns:
            MotionCommand if significant movement detected, None for neutral
        """
        roll = orientation.roll
        pitch = orientation.pitch
        
        # Calculate magnitude to check dead zone
        abs_roll = abs(roll)
        abs_pitch = abs(pitch)
        
        # Check dead zone threshold
        if abs_roll < self.config.dead_zone_threshold and abs_pitch < self.config.dead_zone_threshold:
            return MotionCommand.STOP
        
        # Determine which direction is stronger
        if abs_roll > abs_pitch:
            # Roll is dominant (left-right tilt)
            if roll < -self.config.dead_zone_threshold:
                return MotionCommand.MOVE_LEFT
            elif roll > self.config.dead_zone_threshold:
                return MotionCommand.MOVE_RIGHT
        else:
            # Pitch is dominant (forward-backward tilt)
            if pitch > self.config.dead_zone_threshold:
                return MotionCommand.MOVE_FORWARD
            elif pitch < -self.config.dead_zone_threshold:
                return MotionCommand.MOVE_BACKWARD
        
        return MotionCommand.STOP
    
    def interpret_gesture(self, gesture: WatchGesture) -> 'ActionCommand | None':
        """
        Interpret a gesture into an action command.
        
        Implements debounce logic to avoid repeated triggers.
        
        Args:
            gesture: Detected gesture
        
        Returns:
            ActionCommand if gesture should trigger action, None otherwise
        """
        current_time = gesture.timestamp_ms
        time_since_last = current_time - self._last_gesture_time
        
        # Check debounce window
        if time_since_last < self.config.gesture_debounce_ms:
            self.logger.debug(
                "gesture",
                f"Gesture {gesture.gesture_type} ignored (debounce)"
            )
            return None
        
        self._last_gesture_time = current_time
        
        # Map gesture types to actions
        if gesture.gesture_type.lower() in ("tap", "double_tap"):
            return ActionCommand.PICKUP
        
        return None
    
    def get_command_change(
        self,
        new_motion: 'MotionCommand | None'
    ) -> bool:
        """
        Check if the motion command has changed since last call.
        
        Args:
            new_motion: The newly interpreted motion command
        
        Returns:
            True if command changed, False if it's the same
        """
        if new_motion != self._last_motion_command:
            self._last_motion_command = new_motion
            return True
        return False
