import time

from src.inputs.doublepoint_watch import DoublepointWatchInput


def main():
    watch = DoublepointWatchInput(verbose=True, connection_timeout_s=8.0)

    print("Connecting to real watch...")
    ok = watch.connect()
    if not ok:
        print("FAILED: could not connect to the real watch")
        raise SystemExit(1)

    print("Connected.")
    print("Move your wrist clearly. Tap to test gesture detection.")
    print("Press Ctrl+C to exit.")
    print("")

    last_roll = None
    last_pitch = None

    try:
        while True:
            watch.poll()

            orientation = watch.get_orientation()
            if orientation is not None:
                roll_changed = last_roll is None or abs(orientation.roll - last_roll) >= 3.0
                pitch_changed = last_pitch is None or abs(orientation.pitch - last_pitch) >= 3.0

                if roll_changed or pitch_changed:
                    print(f"orientation: roll={orientation.roll:.1f}, pitch={orientation.pitch:.1f}")
                    last_roll = orientation.roll
                    last_pitch = orientation.pitch

            gesture = watch.get_gesture()
            if gesture is not None:
                print(f"gesture: {gesture.gesture_type}")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        watch.disconnect()


if __name__ == "__main__":
    main()