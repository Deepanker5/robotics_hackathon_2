"""
Real watch input source.

This bridges a real watch SDK into the existing WatchInputSource interface.
"""

import math
import threading
import time
from collections import deque
from typing import Optional, Any

from src.inputs.watch_input import WatchInputSource, WatchOrientation, WatchGesture

try:
    from touch_sdk import Watch as TouchSDKWatch
except Exception:
    TouchSDKWatch = None


def _read_value(obj: Any, *names: str) -> Any:
    """Read a value from an object or dict using multiple possible field names."""
    if obj is None:
        return None

    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj[name]
        return None

    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)

    return None


def _extract_quaternion_parts(q: Any) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """Try to extract quaternion parts as w, x, y, z."""
    if q is None:
        return None, None, None, None

    if isinstance(q, (list, tuple)) and len(q) == 4:
        # Assume [w, x, y, z]
        return float(q[0]), float(q[1]), float(q[2]), float(q[3])

    w = _read_value(q, "w", "qw", "q0")
    x = _read_value(q, "x", "qx", "q1")
    y = _read_value(q, "y", "qy", "q2")
    z = _read_value(q, "z", "qz", "q3")

    if None not in (w, x, y, z):
        return float(w), float(x), float(y), float(z)

    return None, None, None, None


def _quat_to_roll_pitch_deg(w: float, x: float, y: float, z: float) -> tuple[float, float]:
    """Convert quaternion to roll and pitch in degrees."""
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

    sinp = 2.0 * (w * y - z * x)
    sinp = max(-1.0, min(1.0, sinp))
    pitch = math.degrees(math.asin(sinp))

    return roll, pitch


def _extract_orientation(sensors: Any) -> Optional[WatchOrientation]:
    """
    Try several common ways to get roll/pitch from the SDK sensor payload.
    """

    # Case 1: direct roll/pitch on sensors
    roll = _read_value(sensors, "roll")
    pitch = _read_value(sensors, "pitch")
    if roll is not None and pitch is not None:
        return WatchOrientation(roll=float(roll), pitch=float(pitch))

    # Case 2: quaternion nested under sensors.orientation
    q = _read_value(sensors, "orientation", "quaternion")
    w, x, y, z = _extract_quaternion_parts(q)
    if None not in (w, x, y, z):
        roll_deg, pitch_deg = _quat_to_roll_pitch_deg(w, x, y, z)
        return WatchOrientation(roll=roll_deg, pitch=pitch_deg)

    # Case 3: accelerometer fallback
    accel = _read_value(sensors, "accel", "accelerometer")
    if accel is not None:
        ax = _read_value(accel, "x", "ax")
        ay = _read_value(accel, "y", "ay")
        az = _read_value(accel, "z", "az")
        if None not in (ax, ay, az):
            ax = float(ax)
            ay = float(ay)
            az = float(az)

            # Simple gravity-based estimate
            roll_deg = math.degrees(math.atan2(ax, az if abs(az) > 1e-6 else 1e-6))
            pitch_deg = math.degrees(math.atan2(ay, math.sqrt(ax * ax + az * az)))
            return WatchOrientation(roll=roll_deg, pitch=pitch_deg)

    return None


def _normalize_gesture_name(gesture: Any) -> str:
    """Convert gesture enum/object/string into a normalized string."""
    if gesture is None:
        return ""

    name = getattr(gesture, "name", None)
    if name is None:
        name = str(gesture)

    name = name.strip().lower()

    # Ignore empty / idle / no-op gesture events
    if name in ("", "none", "null", "idle", "no_gesture", "unknown"):
        return ""

    # Normalize common tap-like names into the existing interpreter input
    if "tap" in name or "pinch" in name:
        return "tap"

    return name


class DoublepointWatchInput(WatchInputSource):
    """Real watch input adapter."""

    def __init__(self, verbose: bool = False, connection_timeout_s: float = 8.0):
        self._verbose = verbose
        self._connection_timeout_s = connection_timeout_s

        self._connected = False
        self._started = False
        self._connect_error: Optional[Exception] = None

        self._orientation: Optional[WatchOrientation] = None
        self._gesture_queue: deque[WatchGesture] = deque()

        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._sdk_watch = None
        self._saw_first_sensor_packet = False
        self._printed_first_sensor_debug = False

        self._roll_offset = 0.0
        self._pitch_offset = 0.0
        self._calibration_samples = []
        self._is_calibrated = False

    def connect(self) -> bool:
        if TouchSDKWatch is None:
            raise RuntimeError(
                "touch_sdk is not installed. Run: python -m pip install touch-sdk"
            )

        outer = self

        class _SDKBridge(TouchSDKWatch):
            def on_sensors(self_inner, sensors):
                outer._handle_sensors(sensors)

            def on_gesture(self_inner, gesture):
                outer._handle_gesture(gesture)

        def _runner():
            try:
                outer._sdk_watch = _SDKBridge()
                outer._started = True
                outer._sdk_watch.start()
            except Exception as e:
                outer._connect_error = e
                outer._connected = False

        self._thread = threading.Thread(target=_runner, daemon=True)
        self._thread.start()

        deadline = time.time() + self._connection_timeout_s
        while time.time() < deadline:
            if self._connect_error is not None:
                raise RuntimeError(f"Watch connection failed: {self._connect_error}")
            if self._is_calibrated:
                self._connected = True
                if self._verbose:
                    print("[DoublepointWatch] Connected")
                return True
            time.sleep(0.05)

        return False

    def disconnect(self) -> None:
        self._connected = False

        sdk_watch = self._sdk_watch
        self._sdk_watch = None

        try:
            if sdk_watch is not None and hasattr(sdk_watch, "stop"):
                try:
                    sdk_watch.stop()
                except Exception:
                    pass
        finally:
            if self._verbose:
                print("[DoublepointWatch] Disconnected")

    def is_connected(self) -> bool:
        return self._connected

    def get_orientation(self) -> Optional[WatchOrientation]:
        with self._lock:
            return self._orientation

    def get_gesture(self) -> Optional[WatchGesture]:
        with self._lock:
            if not self._gesture_queue:
                return None
            return self._gesture_queue.popleft()

    def poll(self) -> None:
        if self._connect_error is not None:
            raise self._connect_error

        if self._thread is not None and not self._thread.is_alive() and not self._connected:
            raise ConnectionError("Watch thread stopped")

    def _handle_sensors(self, sensors: Any) -> None:
        orientation = _extract_orientation(sensors)

        if orientation is None:
            return

        # Collect initial samples to define neutral wrist pose
        if not self._is_calibrated:
            self._calibration_samples.append((orientation.roll, orientation.pitch))

            if len(self._calibration_samples) >= 20:
                avg_roll = sum(r for r, _ in self._calibration_samples) / len(self._calibration_samples)
                avg_pitch = sum(p for _, p in self._calibration_samples) / len(self._calibration_samples)

                self._roll_offset = avg_roll
                self._pitch_offset = avg_pitch
                self._is_calibrated = True

                if self._verbose:
                    print(
                        f"[DoublepointWatch] Calibrated neutral pose: "
                        f"roll_offset={self._roll_offset:.1f}, pitch_offset={self._pitch_offset:.1f}"
                    )

        corrected = WatchOrientation(
            roll=orientation.roll - self._roll_offset,
            pitch=orientation.pitch - self._pitch_offset,
        )

        with self._lock:
            self._orientation = corrected
            self._saw_first_sensor_packet = True
            self._connected = True

        if self._verbose and not self._printed_first_sensor_debug:
            self._printed_first_sensor_debug = True
            print("[DoublepointWatch] First sensor packet received")

    def _handle_gesture(self, gesture: Any) -> None:
        gesture_name = _normalize_gesture_name(gesture)
        if not gesture_name:
            return

        event = WatchGesture(
            gesture_type=gesture_name,
            timestamp_ms=int(time.time() * 1000),
        )

        with self._lock:
            self._gesture_queue.append(event)

        if self._verbose:
            print(f"[DoublepointWatch] Gesture: {gesture_name}")