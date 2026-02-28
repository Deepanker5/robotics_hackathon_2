"""
Manual Control Subsystem for LeKiwi + SO-101 Robot

Main entry point for the application.
"""

import sys
import argparse
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config import get_default_config
from src.inputs.mock_watch import MockWatchInput
from src.inputs.doublepoint_watch import DoublepointWatchInput
from src.interpreter.watch_interpreter import WatchInterpreter
from src.robot.backend import MockRobotBackend
from src.controller.manual_controller import ManualController
from src.utils.logger import Logger


def create_app(mock_mode: bool = False, verbose: bool = False):
    """
    Create and initialize the application.
    """
    config = get_default_config(mock_mode=mock_mode, verbose=verbose)
    logger = Logger("ManualControl", verbose=verbose)

    if mock_mode:
        watch_input = MockWatchInput(verbose=verbose)
    else:
        watch_input = DoublepointWatchInput(
            verbose=verbose,
            connection_timeout_s=config.watch_input.connection_timeout_s,
        )

    interpreter = WatchInterpreter(config.watch_input, logger)
    robot_backend = MockRobotBackend(logger)

    controller = ManualController(
        config=config,
        watch_input=watch_input,
        interpreter=interpreter,
        robot_backend=robot_backend,
        logger=logger,
    )

    return controller, logger


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manual control subsystem for LeKiwi + SO-101 robot"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=False,
        help="Run in mock/dry-run mode",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    try:
        controller, logger = create_app(mock_mode=args.mock, verbose=args.verbose)

        logger.info("main", "=" * 60)
        logger.info("main", "Manual Control System Starting")
        logger.info("main", "=" * 60)
        logger.info("main", f"Mode: {'MOCK/DRY-RUN' if args.mock else 'REAL WATCH INPUT'}")
        logger.info("main", f"Verbose: {args.verbose}")
        logger.info("main", "")
        logger.info("main", "Watch Input:")
        logger.info("main", "  - Tilt wrist LEFT  -> drive left")
        logger.info("main", "  - Tilt wrist RIGHT -> drive right")
        logger.info("main", "  - Tilt wrist FWD   -> drive forward")
        logger.info("main", "  - Tilt wrist BACK  -> drive backward")
        logger.info("main", "  - Tap gesture      -> pickup action")
        logger.info("main", "")
        logger.info("main", "Press Ctrl+C to exit")
        logger.info("main", "=" * 60)
        logger.info("main", "")

        controller.run()
        return 0

    except KeyboardInterrupt:
        print()
        return 0
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())