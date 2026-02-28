"""
Logger utility for clean, non-noisy logging.
"""

import sys
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log levels."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Logger:
    """Simple logger that avoids noisy repeated messages."""
    
    def __init__(self, name: str, verbose: bool = False):
        self.name = name
        self.verbose = verbose
        self.min_level = LogLevel.DEBUG if verbose else LogLevel.INFO
        self._last_messages: dict[str, str] = {}
    
    def _format_message(self, level: LogLevel, category: str, message: str) -> str:
        """Format a log message with timestamp and level."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        level_str = level.name.upper()
        return f"[{timestamp}] [{level_str}] [{self.name}:{category}] {message}"
    
    def debug(self, category: str, message: str) -> None:
        """Log a debug message."""
        if self.min_level.value <= LogLevel.DEBUG.value:
            print(self._format_message(LogLevel.DEBUG, category, message))
    
    def info(self, category: str, message: str, suppress_duplicate: bool = False) -> None:
        """
        Log an info message.
        
        Args:
            category: Message category for grouping
            message: Message to log
            suppress_duplicate: If True, don't log if same message was just logged
        """
        if self.min_level.value <= LogLevel.INFO.value:
            if suppress_duplicate:
                key = f"{category}:{message}"
                if key in self._last_messages and self._last_messages[key] == message:
                    return
                self._last_messages[key] = message
            
            print(self._format_message(LogLevel.INFO, category, message))
    
    def warning(self, category: str, message: str) -> None:
        """Log a warning message."""
        if self.min_level.value <= LogLevel.WARNING.value:
            print(self._format_message(LogLevel.WARNING, category, message), file=sys.stderr)
    
    def error(self, category: str, message: str) -> None:
        """Log an error message."""
        if self.min_level.value <= LogLevel.ERROR.value:
            print(self._format_message(LogLevel.ERROR, category, message), file=sys.stderr)
