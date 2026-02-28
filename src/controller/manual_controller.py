"""
Main controller that orchestrates the manual control system.
"""

import time
from src.config import AppConfig
from src.inputs.watch_input import WatchInputSource
from src.interpreter.watch_interpreter import WatchInterpreter
from src.robot.backend import RobotBackend
from src.utils.commands import MotionCommand, ActionCommand, RobotCommand
from src.utils.logger import Logger


class ManualController:
    """
    Orchestrates the manual control loop.
    
    Responsibilities:
    - Connect watch input
    - Poll watch for data
    - Interpret watch data into commands
    - Execute commands via robot backend
    - Handle safe shutdown
    """
    
    def __init__(
        self,
        config: AppConfig,
        watch_input: WatchInputSource,
        interpreter: WatchInterpreter,
        robot_backend: RobotBackend,
        logger: Logger,
    ):
        """
        Initialize the controller.
        
        Args:
            config: Application configuration
            watch_input: Watch input source
            interpreter: Command interpreter
            robot_backend: Robot backend
            logger: Logger instance
        """
        self.config = config
        self.watch_input = watch_input
        self.interpreter = interpreter
        self.robot_backend = robot_backend
        self.logger = logger
        
        self._running = False
        self._last_command: 'RobotCommand | None' = None
        self._last_heartbeat = 0.0
    
    def connect(self) -> bool:
        """
        Connect to the watch.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info("controller", "Connecting to watch...")
            if not self.watch_input.connect():
                self.logger.error("controller", "Failed to connect to watch")
                return False
            
            self.logger.info("controller", "Watch connected successfully")
            return True
        except Exception as e:
            self.logger.error("controller", f"Connection error: {e}")
            return False
    
    def _should_emit_heartbeat(self) -> bool:
        """Check if a heartbeat log should be emitted."""
        if self.config.heartbeat_interval_s <= 0:
            return False
        
        current_time = time.time()
        if current_time - self._last_heartbeat >= self.config.heartbeat_interval_s:
            self._last_heartbeat = current_time
            return True
        
        return False
    
    def _process_watch_data(self) -> None:
        """
        Poll watch data and execute resulting commands.
        
        Raises:
            ConnectionError: If watch disconnects
        """
        try:
            self.watch_input.poll()
        except Exception as e:
            self.logger.error("watch", f"Poll error: {e}")
            raise ConnectionError("Watch disconnected") from e
        
        if not self.watch_input.is_connected():
            raise ConnectionError("Watch disconnected")
        
        # Get current orientation and interpret it
        orientation = self.watch_input.get_orientation()
        if orientation is None:
            return
        
        new_motion = self.interpreter.interpret_orientation(orientation)
        
        # Check if motion command changed
        if self.interpreter.get_command_change(new_motion):
            if new_motion:
                cmd = RobotCommand(motion=new_motion)
                self._execute_command(cmd)
        elif self._should_emit_heartbeat():
            if new_motion:
                self.logger.debug("heartbeat", f"Current motion: {new_motion.name}")
        
        # Check for gestures
        gesture = self.watch_input.get_gesture()
        if gesture:
            action = self.interpreter.interpret_gesture(gesture)
            if action:
                cmd = RobotCommand(action=action)
                self._execute_command(cmd)
    
    def _execute_command(self, cmd: RobotCommand) -> None:
        """
        Execute a robot command.
        
        Args:
            cmd: RobotCommand to execute
        """
        if cmd.motion:
            self.robot_backend.execute_motion(cmd.motion)
        
        if cmd.action:
            self.robot_backend.execute_action(cmd.action)
        
        self._last_command = cmd
    
    def run(self, poll_interval_s: float = 0.05) -> None:
        """
        Run the main control loop.
        
        Args:
            poll_interval_s: Time between watch polls in seconds
        
        Raises:
            KeyboardInterrupt: When user presses Ctrl+C
            RuntimeError: If watch input fails to connect
        """
        if not self.connect():
            raise RuntimeError("Failed to connect to watch")
        
        self._running = True
        self.logger.info("controller", "Manual control system started")
        
        try:
            while self._running:
                try:
                    self._process_watch_data()
                except ConnectionError:
                    self.logger.error("controller", "Watch disconnected, stopping robot")
                    self.robot_backend.stop_all()
                    break
                
                time.sleep(poll_interval_s)
        
        except KeyboardInterrupt:
            self.logger.info("controller", "Shutdown signal received")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Shutdown the control system safely."""
        if not self._running:
            return
        
        self._running = False
        
        try:
            self.logger.info("controller", "Stopping robot...")
            self.robot_backend.stop_all()
            
            '''self.logger.info("controller", "Disconnecting watch...")
            self.watch_input.disconnect()'''
            self.logger.info("controller", "Disconnecting watch...")
            try:
                self.watch_input.disconnect()
            except Exception as e:
                self.logger.error("controller", f"Watch disconnect error: {e}")
            
            self.logger.info("controller", "Shutting down robot backend...")
            self.robot_backend.shutdown()
        except Exception as e:
            self.logger.error("controller", f"Shutdown error: {e}")
        finally:
            self.logger.info("controller", "Manual control system stopped")
