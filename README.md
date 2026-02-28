# Manual Control Subsystem for LeKiwi + SO-101 Robot

A clean, modular Python implementation of the manual control system for the LeKiwi + SO-101 robotics challenge.

**Status**: Ready for local laptop testing in mock mode. Designed for easy integration of real hardware backends later.

---

## Quick Start

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
```

### 2. Activate Virtual Environment

```bash
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

(Currently no external dependencies - pure Python implementation)

### 4. Run in Mock Mode (Dry-Run on Laptop)

```bash
python src/main.py --mock
```

### 5. Run with Verbose Logging

```bash
python src/main.py --mock --verbose
```

### 6. Stop the Application

Press `Ctrl+C` to safely shutdown.

### 7. Deactivate Virtual Environment

```bash
deactivate
```

---

## Mock Mode Behavior

In mock mode, the system simulates:
- Watch input (simulated wrist orientation and gestures)
- Robot motion commands (printed as text)
- Pickup actions (printed as text)

Example console output:

```
[14:32:05.123] [INFO] [ManualControl:main] ============================================================
[14:32:05.124] [INFO] [ManualControl:main] Manual Control System Starting
[14:32:05.124] [INFO] [ManualControl:main] ============================================================
[14:32:05.125] [INFO] [ManualControl:main] Mode: MOCK/DRY-RUN
[14:32:05.126] [INFO] [ManualControl:main] Verbose: False
[14:32:05.127] [INFO] [ManualControl:main] 
[14:32:05.128] [INFO] [ManualControl:main] Watch Input:
[14:32:05.129] [INFO] [ManualControl:main]   - Tilt wrist LEFT  -> drive left
[14:32:05.130] [INFO] [ManualControl:main]   - Tilt wrist RIGHT -> drive right
[14:32:05.131] [INFO] [ManualControl:main]   - Tilt wrist FWD   -> drive forward
[14:32:05.132] [INFO] [ManualControl:main]   - Tilt wrist BACK  -> drive backward
[14:32:05.133] [INFO] [ManualControl:main]   - Tap gesture      -> pickup action
[14:32:05.134] [INFO] [ManualControl:main] 
[14:32:05.135] [INFO] [ManualControl:main] Press Ctrl+C to exit
[14:32:05.136] [INFO] [ManualControl:main] ============================================================
[14:32:05.137] [INFO] [ManualControl:main] 
[14:32:05.138] [INFO] [ManualControl:controller] Connecting to watch...
[14:32:05.139] [INFO] [ManualControl:controller] Watch connected successfully
[14:32:05.140] [INFO] [ManualControl:controller] Manual control system started
[14:32:05.142] [INFO] [ManualControl:robot] 🤖 driving forward
[14:32:05.245] [INFO] [ManualControl:robot] 🤖 driving left
[14:32:05.348] [INFO] [ManualControl:robot] 🤖 stopping base
```

---

## Project Architecture

### Directory Structure

```
robotics_hackathon_2/
├── .venv/                    # Virtual environment (auto-created)
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Configuration & constants
│   ├── inputs/              # Watch input layer
│   │   ├── __init__.py
│   │   ├── watch_input.py  # Abstract interface
│   │   └── mock_watch.py   # Mock implementation for testing
│   ├── interpreter/         # Interpretation layer
│   │   ├── __init__.py
│   │   └── watch_interpreter.py  # Converts wrist data to commands
│   ├── robot/              # Robot backend layer
│   │   ├── __init__.py
│   │   └── backend.py      # Abstract + mock implementation
│   ├── controller/         # Main orchestration
│   │   ├── __init__.py
│   │   └── manual_controller.py
│   └── utils/              # Shared utilities
│       ├── __init__.py
│       ├── logger.py       # Non-noisy logging
│       └── commands.py     # Command definitions
├── .gitignore
├── requirements.txt        # Dependencies (empty for pure Python)
├── README.md              # This file
├── specs.md               # Full specifications
└── copilot_prompt.md      # Original instructions
```

### Module Responsibilities

| Module | Responsibility |
|--------|-----------------|
| `inputs/watch_input.py` | Abstract interface for watch input sources |
| `inputs/mock_watch.py` | Mock watch implementation (random orientation, gesture injection) |
| `interpreter/watch_interpreter.py` | Converts raw wrist orientation/gestures into semantic commands |
| `robot/backend.py` | Abstract robot interface + mock implementation |
| `controller/manual_controller.py` | Main event loop, coordinates all components |
| `utils/logger.py` | Avoids noisy repeated logs |
| `utils/commands.py` | Command definitions (MotionCommand, ActionCommand) |
| `config.py` | All thresholds and tunable parameters |

---

## Key Design Features

### ✅ Modular & Testable
- Clean separation of concerns (input → interpretation → execution)
- Mock implementations for laptop testing without hardware
- Interfaces clearly defined for future replacement

### ✅ Safe Shutdown
- Graceful `KeyboardInterrupt` handling
- Watch disconnect detection and safe robot stop
- No background threads or leaked resources
- Explicit resource cleanup in `shutdown()`

### ✅ Non-Noisy Logging
- Commands only logged when state changes
- Optional heartbeat logging for monitoring
- Structured logging with categories

### ✅ Integration-Ready
- Clear integration points for real hardware:
  - Replace `MockWatchInput` with real Doublepoint driver
  - Replace `MockRobotBackend` with real LeKiwi/SO-101 driver
  - Add ACT policy callback in action execution
- No tight coupling to mock implementations

### ✅ Configuration-Driven
- All thresholds in `config.py`
- Dead zone for wrist orientation filtering
- Gesture debounce to prevent repeated triggers
- Easy to tune for different hardware

---

## Command Mappings

### Wrist Orientation → Motion Commands

| Wrist Tilt | Command | Result |
|-----------|---------|--------|
| Forward (pitch > 15°) | `MOVE_FORWARD` | Drive forward |
| Backward (pitch < -15°) | `MOVE_BACKWARD` | Drive backward |
| Left (roll < -15°) | `MOVE_LEFT` | Drive left |
| Right (roll > 15°) | `MOVE_RIGHT` | Drive right |
| Neutral (< 15°) | `STOP` | Stop base |

### Gestures → Action Commands

| Gesture | Command | Result |
|---------|---------|--------|
| Tap | `PICKUP` | Trigger pickup/ACT policy |
| Double-tap | `PICKUP` | Trigger pickup/ACT policy |

---

## Integration Guide

### To Use Real Hardware

1. **Doublepoint Watch Input:**
   - Create `RealWatchInput(WatchInputSource)` in new file `src/inputs/real_watch.py`
   - Implement connection to Doublepoint SDK
   - Return real orientation/gesture data
   - Update `main.py` to use `RealWatchInput` instead of `MockWatchInput`

2. **LeKiwi + SO-101 Robot Backend:**
   - Create `RealRobotBackend(RobotBackend)` in new file `src/robot/real_backend.py`
   - Implement motion commands (move_forward, move_left, etc.)
   - Implement pickup trigger to call ACT policy
   - Update `main.py` to use `RealRobotBackend` instead of `MockRobotBackend`

3. **ACT Policy Integration:**
   - In `RealRobotBackend.execute_action(ActionCommand.PICKUP)`:
     - Call ACT policy inference function
     - Pass robot state to ACT policy
     - Execute resulting arm/gripper commands

Example template:

```python
# src/robot/real_backend.py
class RealRobotBackend(RobotBackend):
    def execute_action(self, command: ActionCommand) -> None:
        if command == ActionCommand.PICKUP:
            # Call your ACT policy module
            from act_policy import pickup_inference
            result = pickup_inference(robot_state=self.get_robot_state())
            # Execute the result
            self.arm_controller.execute(result)
```

---

## Configuration Tuning

Edit `src/config.py` to adjust behavior:

```python
@dataclass
class WatchInputConfig:
    dead_zone_threshold: float = 15.0          # Tilt angle to trigger motion
    orientation_change_threshold: float = 5.0  # Min change to register movement
    gesture_debounce_ms: int = 200             # Prevent repeated gestures
    connection_timeout_s: float = 5.0          # Watch connection timeout
```

---

## Testing Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (none required)
- [ ] `python src/main.py --mock` starts successfully
- [ ] Console output appears with proper formatting
- [ ] `Ctrl+C` exits cleanly
- [ ] Deactivate works: `deactivate`
- [ ] Project folder can be deleted cleanly

---

## Troubleshooting

**Issue**: Python not found
- Solution: Ensure `.venv` is activated (`source .venv/bin/activate`)

**Issue**: Module import errors
- Solution: Ensure you're running from project root: `cd /Users/deepanker/Desktop/robotics_hackathon_2`

**Issue**: Application hangs on disconnect
- Solution: Press `Ctrl+C` - should exit cleanly within 1 second

**Issue**: Noisy repeated logs
- Solution: Run without `--verbose` flag, or adjust `heartbeat_interval_s` in config

---

## Files Overview

| File | Purpose |
|------|---------|
| `src/main.py` | Entry point, CLI argument parsing, app initialization |
| `src/config.py` | Configuration dataclasses and defaults |
| `src/inputs/watch_input.py` | Abstract watch input interface |
| `src/inputs/mock_watch.py` | Mock watch for testing |
| `src/interpreter/watch_interpreter.py` | Converts orientation/gesture to commands |
| `src/robot/backend.py` | Abstract robot interface + mock |
| `src/controller/manual_controller.py` | Main control loop |
| `src/utils/logger.py` | Non-noisy logging |
| `src/utils/commands.py` | Command enums |
| `requirements.txt` | Dependencies (empty - pure Python) |
| `.gitignore` | Git ignore rules |

---

## Next Steps

1. ✅ **Phase 1: Mock Mode** (current)
   - Test locally on laptop
   - Verify command flow and shutdown safety
   - Iterate on thresholds and debounce

2. **Phase 2: Hardware Integration**
   - Implement `RealWatchInput` with Doublepoint SDK
   - Implement `RealRobotBackend` with LeKiwi/SO-101 drivers
   - Add ACT policy callback

3. **Phase 3: Integration Testing**
   - Test on actual robot
   - Calibrate thresholds for real hardware
   - Stress test for robustness

---

## License & Attribution

Part of the LeKiwi + SO-101 robotics hackathon project.

---

## Support

For questions or issues:
1. Check `specs.md` for detailed requirements
2. Review module docstrings for API details
3. Run with `--verbose` flag for debug output
