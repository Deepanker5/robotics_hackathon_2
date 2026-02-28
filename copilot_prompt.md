You are implementing the manual control subsystem for a LeKiwi + SO-101 robot project.

Read and follow the `specs.md` file in this repository as the source of truth.

Your task is to generate the full initial project codebase for the manual control subsystem only.

## What to do

1. Create the full project structure.
2. Implement a modular Python codebase.
3. Use a virtual-environment-friendly setup.
4. Make the system runnable on a normal laptop in mock / dry-run mode without real robot hardware.
5. Keep the design integration-friendly so real hardware backends can be swapped in later.
6. Prioritize safe shutdown, low complexity, clear interfaces, and production-minded code.

## Important constraints

- Do not implement the ACT policy itself.
- Do not implement Gemini integration.
- Do not implement throw/store logic.
- Only implement the manual control subsystem and the interfaces/hooks needed for future integration.
- If Doublepoint SDK details are unknown, create an adapter interface plus a mock implementation.
- The code must be easy to test locally using console output.
- The code must avoid noisy repeated logs when the command state has not changed.
- The code must stop safely on disconnect, invalid input, exceptions, or shutdown.

## Output requirements

Please generate:

- `README.md`
- `requirements.txt`
- `.gitignore`
- `src/main.py`
- `src/config.py`
- modules for input handling, interpretation, robot backend, controller, and utilities
- a mock backend for local laptop testing
- clear setup/run instructions

## Coding requirements

- Use Python
- Use type hints
- Keep dependencies minimal
- Use simple, readable architecture
- Add docstrings where useful
- Avoid overengineering
- Prefer explicit interfaces and small modules
- Make cleanup reliable

## Implementation strategy

- Start with the mock / dry-run path first.
- Build clean interfaces for:
  - watch input source
  - motion command sink
  - pickup action trigger
- Add a mock watch input generator if needed for local testing.
- Add a command-line flag like `--mock` or `--dry-run`.
- Ensure the app exits cleanly with `KeyboardInterrupt`.

## Deliver the code in a way that a human can immediately run it

Include the exact commands for:

1. creating a virtual environment
2. activating it
3. installing dependencies
4. running the app
5. deactivating the environment

Now start implementing the project.
