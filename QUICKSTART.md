# Quick Start Guide

## One-Time Setup (First Run)

```bash
# Navigate to project directory
cd /Users/deepanker/Desktop/robotics_hackathon_2

# Create Python virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies (none required, but good practice)
pip install -r requirements.txt
```

**Verify setup:**
```bash
which python  # Should show: /Users/deepanker/Desktop/robotics_hackathon_2/.venv/bin/python
which pip     # Should show: /Users/deepanker/Desktop/robotics_hackathon_2/.venv/bin/pip
```

---

## Running the System

### Mode 1: Mock Mode (Testing on Laptop - No Hardware)

```bash
# Basic run (quiet mode)
python src/main.py --mock

# With verbose logging (see all debug messages)
python src/main.py --mock --verbose
```

### What to Expect

The system will:
1. Show initialization messages
2. Connect to the mock watch
3. Continuously poll for watch data
4. Print commands when wrist orientation changes
5. Print action messages when gestures are detected
6. Exit cleanly when you press `Ctrl+C`

**Example output:**
```
[20:40:46.064] [INFO] [ManualControl:controller] Connecting to watch...
[20:40:46.064] [INFO] [ManualControl:controller] Watch connected successfully
[20:40:46.064] [INFO] [ManualControl:controller] Manual control system started
[20:40:46.064] [INFO] [ManualControl:robot] 🤖 driving forward
```

### Mode 2: Verbose Testing with Simulated Input

```bash
# Run the test script
python test_mock.py
```

This script:
- Initializes the system
- Injects simulated watch data
- Shows how commands are interpreted
- Demonstrates pickup action

---

## Cleanup

```bash
# Stop the application
# Press Ctrl+C in the terminal

# Deactivate virtual environment
deactivate

# (Optional) Remove the entire project folder when done
rm -rf /Users/deepanker/Desktop/robotics_hackathon_2
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found: python` | Use `/Users/deepanker/Desktop/robotics_hackathon_2/.venv/bin/python` or activate venv |
| `ModuleNotFoundError: No module named 'src'` | Run from project root: `cd /Users/deepanker/Desktop/robotics_hackathon_2` |
| Application hangs | Press `Ctrl+C` - should exit cleanly within 1 second |
| Port already in use (if running on real hardware) | Change port in `src/config.py` or stop other instances |

---

## File Structure Quick Reference

```
/Users/deepanker/Desktop/robotics_hackathon_2/
├── .venv/                          # Virtual environment (auto-created)
├── src/
│   ├── main.py                    # Entry point - run this
│   ├── config.py                  # Configuration constants
│   ├── inputs/                    # Watch input layer
│   │   ├── watch_input.py        # Abstract interface
│   │   └── mock_watch.py         # Mock implementation
│   ├── interpreter/               # Interpretation layer
│   │   └── watch_interpreter.py  # Orientation → Commands
│   ├── robot/                    # Robot backend layer
│   │   └── backend.py            # Abstract + Mock implementation
│   ├── controller/               # Main orchestration
│   │   └── manual_controller.py  # Event loop & coordination
│   └── utils/                    # Utilities
│       ├── logger.py             # Non-noisy logging
│       └── commands.py           # Command definitions
├── .gitignore
├── requirements.txt              # Dependencies (empty - pure Python)
├── README.md                     # Full documentation
├── specs.md                      # Requirements specification
└── test_mock.py                  # Test script
```

---

## Key Commands for Development

| Command | Purpose |
|---------|---------|
| `python src/main.py --help` | Show command-line options |
| `python src/main.py --mock` | Run in test mode |
| `python src/main.py --mock --verbose` | Run with debug output |
| `python test_mock.py` | Run automated test |
| `deactivate` | Exit virtual environment |

---

## Integration with Real Hardware

When ready to integrate real hardware:

1. Create `src/inputs/real_watch.py` with Doublepoint SDK connection
2. Create `src/robot/real_backend.py` with LeKiwi/SO-101 drivers
3. Update `src/main.py` to use real implementations instead of mock
4. Replace `MockWatchInput` with `RealWatchInput`
5. Replace `MockRobotBackend` with `RealRobotBackend`

See README.md for detailed integration guide.

---

## Configuration Tuning

Edit `src/config.py` to adjust:

- **dead_zone_threshold**: Minimum wrist tilt to trigger motion (degrees)
- **gesture_debounce_ms**: Time to wait between gesture triggers
- **heartbeat_interval_s**: Debug logging interval (seconds)

---

## Support

- **Questions?** See `README.md` for full documentation
- **Need specs?** Check `specs.md` for requirements
- **Code structure?** Each module has detailed docstrings
