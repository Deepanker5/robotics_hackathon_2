"""
Robot backend interfaces and implementations.
"""

from abc import ABC, abstractmethod
from src.utils.commands import MotionCommand, ActionCommand
from src.utils.logger import Logger


class RobotBackend(ABC):
    """Abstract base class for robot backends."""
    
    @abstractmethod
    def execute_motion(self, command: MotionCommand) -> None:
        """
        Execute a motion command.
        
        Args:
            command: MotionCommand to execute
        """
        pass
    
    @abstractmethod
    def execute_action(self, command: ActionCommand) -> None:
        """
        Execute an action command.
        
        Args:
            command: ActionCommand to execute
        """
        pass
    
    @abstractmethod
    def stop_all(self) -> None:
        """Stop all motion and actions immediately."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Cleanly shutdown the robot backend."""
        pass


class MockRobotBackend(RobotBackend):
    """
    Mock robot backend that prints commands to console.
    
    Used for local laptop testing without real hardware.
    """
    
    def __init__(self, logger: Logger):
        """
        Initialize mock backend.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self._stopped = False
    
    def execute_motion(self, command: MotionCommand) -> None:
        """Print motion command."""
        if command == MotionCommand.MOVE_FORWARD:
            self.logger.info("robot", "🤖 driving forward", suppress_duplicate=True)
        elif command == MotionCommand.MOVE_BACKWARD:
            self.logger.info("robot", "🤖 driving backward", suppress_duplicate=True)
        elif command == MotionCommand.MOVE_LEFT:
            self.logger.info("robot", "🤖 driving left", suppress_duplicate=True)
        elif command == MotionCommand.MOVE_RIGHT:
            self.logger.info("robot", "🤖 driving right", suppress_duplicate=True)
        elif command == MotionCommand.STOP:
            self.logger.info("robot", "🤖 stopping base", suppress_duplicate=True)
    
    def execute_action(self, command: ActionCommand) -> None:
        """Print action command."""
        if command == ActionCommand.PICKUP:
            self.logger.info("robot", "🤖 ACT policy activated (pickup)")
    
    def stop_all(self) -> None:
        """Stop all motion."""
        self._stopped = True
        self.logger.info("robot", "🤖 emergency stop engaged")
    
    def shutdown(self) -> None:
        """Shutdown the backend."""
        self._stopped = True
        self.logger.info("robot", "🤖 robot backend shutdown")
