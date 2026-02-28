# Manual Control System Spec for LeKiwi + SO-101 Robot

## Context

I am building a robotics project for the following challenge:

**Challenge 2**  
Automate the most impressive task using **one LeRobot SO-101 arm** mounted on an **omnidirectional LeKiwi platform**, powered by a **Jetson Orin Nano**, using robot learning techniques such as RL, VLA, imitation learning, or similar methods.

The full robot system consists of:

- **LeRobot SO-101 arm**
- **LeKiwi omnidirectional mobile platform**
- **Jetson Orin Nano** as the onboard computer / controller

The Jetson is intended to act as the robot’s main brain and control both:

- **base movement** of the LeKiwi platform
- **manipulation** of the SO-101 arm

## Larger system architecture

We plan to run **Gemini 3.5 Flash** on the Jetson as the **high-level controller**.

That controller will have access to the following robot capabilities / tools:

1. **ACT policy**
   - likely based on a Hugging Face implementation
   - will be fine-tuned to detect and pick up visible objects
   - after pickup, the robot should hold the object

2. **Hardcoded `throw` command**
   - used to throw the currently held object
   - example use case: playing fetch with a pet

3. **Hardcoded `store` command**
   - used to place the currently held object into a basket attached to the robot
   - example use case: cleaning up a space

## Robot modes

The robot has **two operating modes**.

### 1. Autonomous mode
This uses:

- Gemini 3.5 Flash as the high-level controller
- ACT policy for pickup
- hardcoded `throw` and `store` commands

### 2. Manual mode
This is the part I need implemented now.

Manual mode should allow a user to control the robot via a **Doublepoint Developer Kit** smartwatch interface.

## Manual mode behavior

The user wears the smartwatch normally. Wrist orientation should map to robot movement as follows:

- **tilt wrist left** -> drive left
- **tilt wrist right** -> drive right
- **tilt wrist forward** -> drive forward
- **tilt wrist backward** -> drive backward

In addition:

- a **tap / finger gesture** should trigger the robot’s **pickup action**
- this pickup action should conceptually map to the same pickup capability used in autonomous mode
- for now, since the ACT policy integration is being built by someone else, triggering pickup can call a placeholder integration hook

## Important implementation constraints

Another teammate is already handling:

- ACT policy training
- hardcoded `throw` and `store` commands
- Gemini 3.5 Flash integration

My task is **only the manual control subsystem**.

I want the code for manual control to be designed so that it can later be integrated into the larger robot stack with **little to no modification**.

## Very important development requirement

I want this developed in a way that is easy to remove cleanly from my laptop after the project is done.

So:

- use a **Python virtual environment** or another isolated dependency setup
- do **not** rely on polluting the global Python environment
- include a clear setup process where I can later delete the project folder / virtual environment and my laptop returns to its prior state
- if any packages are required, list them clearly in `requirements.txt`
- keep the project self-contained

## Local laptop testing requirement

I want to be able to test the manual control system **without the physical robot connected**.

That means the code should support a **simulation / dry-run mode** where robot actions are replaced by simple console outputs such as:

- `"driving left"`
- `"driving right"`
- `"driving forward"`
- `"driving backward"`
- `"stopping base"`
- `"ACT policy activated"`
- `"watch disconnected, stopping robot"`

This local test mode is very important. I want to verify that:

- watch inputs are being read correctly
- wrist orientation is being interpreted correctly
- gesture detection works
- command routing works
- startup and shutdown work safely

## Primary objective

Build the **manual control subsystem** only.

It should:

- read watch input from the Doublepoint Developer Kit
- interpret orientation and gestures
- convert them into clean motion / action commands
- expose interfaces that can later connect to real robot drivers and the ACT policy stack
- support local dry-run testing without real hardware
- shut down cleanly and safely

---

# What I want you to build

## Deliverables

Please create the following:

### 1. Project structure
A clean, minimal project structure, for example:

- `README.md`
- `requirements.txt`
- `.gitignore`
- `src/`
  - `main.py`
  - `config.py`
  - `controller/`
  - `inputs/`
  - `interpreters/`
  - `robot/`
  - `utils/`

You may adjust the structure if you have a better idea, but keep it simple and modular.

### 2. Setup instructions
Provide setup instructions using a **virtual environment**.

For example, something like:

- create virtual environment
- activate it
- install requirements
- run the program
- deactivate environment when done

The instructions should make cleanup trivial.

### 3. Manual control code
Implement the manual control system in a modular way.

### 4. Dry-run / mock mode
Implement a mode that works on a normal laptop without the robot connected, where robot outputs are printed to the console instead of sent to hardware.

### 5. Integration-friendly interfaces
Create explicit interfaces / abstractions so the mock implementation can later be replaced by actual robot drivers and ACT policy calls.

---

# Technical requirements

## Architecture requirements

The code should be broken into clearly separated components.

At minimum, separate the following concerns:

### A. Watch input layer
Responsible for:

- receiving raw data from the Doublepoint Developer Kit
- handling connection / disconnection
- exposing raw orientation / gesture events

### B. Interpretation layer
Responsible for:

- converting raw watch orientation into semantic commands like:
  - `MOVE_LEFT`
  - `MOVE_RIGHT`
  - `MOVE_FORWARD`
  - `MOVE_BACKWARD`
  - `STOP`
- converting gestures into action commands like:
  - `PICKUP`

### C. Robot command layer
Responsible for:

- receiving semantic commands
- routing them either to:
  - a mock / print-based robot backend
  - or a future real robot backend

### D. Integration hooks
Responsible for providing stable interfaces for:
- base movement commands
- pickup action trigger
- future ACT policy integration

### E. App lifecycle / orchestration layer
Responsible for:
- startup
- dependency wiring
- event loop
- safe shutdown
- logging

---

# Functional requirements

## Movement
The system should support at least these commands:

- move left
- move right
- move forward
- move backward
- stop

If the wrist returns to neutral or input becomes invalid, the robot should stop.

## Pickup trigger
The system should support a gesture-triggered pickup action.

For now, in mock mode, this can print:

`ACT policy activated`

But the design should make it easy to replace later with a real call such as:

- sending an event
- invoking a callback
- calling an ACT-policy service / module

## Neutral state and dead zone
Do not trigger movement from tiny random wrist changes.

Implement a **dead zone** or threshold so that small orientation noise does not cause motion.

## Command stability
Avoid spamming the same output repeatedly if the interpreted command has not changed.

For example:

- if the robot is already moving right, do not print `"driving right"` every loop iteration
- only emit a new command when the interpreted state changes
- optionally support periodic heartbeat logging if useful, but do not make logs noisy

## Safe failure behavior
If any of the following happens:

- watch disconnects
- invalid sensor data
- unexpected exception in the input pipeline
- shutdown signal received

Then the system should fail safely by:

- stopping robot motion
- cleaning up resources
- exiting cleanly

---

# Reliability requirements

The code should be **safe, robust, and cleanly terminating**.

Please take extra care with:

- avoiding hanging threads
- avoiding background tasks that never stop
- avoiding memory leaks
- avoiding device / socket handles left open
- avoiding robot motion continuing after program exit
- handling `KeyboardInterrupt` cleanly
- handling watch disconnect cleanly
- ensuring any async tasks / loops / threads are stopped properly

If you use threads or async code, keep it simple and make cleanup explicit and reliable.

When the program exits, it should leave the system in a fully stopped state.

---

# Laptop-first development requirement

I will test this on my own laptop first, without the physical robot.

So please assume the following development approach:

## Phase 1
Implement everything using a **mock backend**:
- print movement commands
- print pickup activation
- simulate stop behavior
- allow testing of architecture and command flow

## Phase 2
Make it easy to swap in:
- real LeKiwi movement driver
- real ACT-policy pickup trigger
- real Doublepoint device input connector

This means the code should be written so the mock components and real components share the same interface.

---

# Assumptions you should make

If some hardware protocol details are unknown, do **not** block on that.

Instead:

- define clear interfaces for the unknown parts
- provide mock implementations
- isolate device-specific logic behind adapters
- make reasonable engineering assumptions
- document where real device integration needs to be added later

Do not tightly couple the whole system to undocumented SDK details.

---

# Expected output format

Please produce:

## 1. A short architecture summary
Explain the module boundaries and why the design is easy to integrate later.

## 2. The full code
Provide all necessary files.

## 3. Setup instructions
Use a virtual environment and local run instructions.

## 4. Example output
Show what console output might look like in mock mode.

## 5. Integration notes
Explain exactly where I or my teammate would later connect:
- the real Doublepoint input source
- the real LeKiwi motion controller
- the ACT policy pickup module

---

# Coding style requirements

Please optimize your output for **GitHub Copilot with Claude Haiku 4.5**.

That means:

- keep the requirements explicit
- keep module responsibilities very clear
- avoid vague wording
- prefer simple, readable, production-minded Python
- add type hints
- add docstrings where useful
- avoid overengineering
- avoid unnecessary abstraction layers
- do not introduce large frameworks unless clearly necessary
- keep the design easy for a human teammate to understand quickly

Also:

- use clean naming
- include comments only where they add real value
- keep dependencies minimal
- keep the system self-contained

---

# Acceptance criteria

I will consider the task successful if the result satisfies all of the following:

1. I can create a virtual environment and install dependencies locally.
2. I can run the code on my laptop without the physical robot connected.
3. I can see console outputs corresponding to interpreted watch commands.
4. The architecture cleanly separates input handling, interpretation, robot command execution, and integration hooks.
5. The system safely stops on shutdown or disconnect.
6. The code is easy to integrate later into the larger robot stack.
7. Cleanup is easy: I can delete the project folder / virtual environment and my laptop goes back to normal.

---

# Nice-to-have features

If reasonable, include some of the following:

- config file or constants for motion thresholds
- debounce logic for gesture triggers
- simple logger instead of raw prints
- mock input generator for testing without actual watch hardware
- unit-test-friendly design
- command-line flag like `--mock` or `--dry-run`

---

# Final instruction

Please proceed by implementing the **manual control subsystem only**, with a **mockable, laptop-testable architecture**, using **Python**, **virtual-environment-friendly setup**, and **safe shutdown behavior**.

If real hardware details are missing, create well-designed interfaces and mock implementations rather than stalling.
