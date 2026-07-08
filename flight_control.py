import math

from data_classes import TelemetryData, ControllerCommand
from geometry_helpers import relative_vector, desired_yaw, yaw_error


def clamp(value, minimum=-1.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def process_telemetry_data(data: TelemetryData) -> ControllerCommand:
    """
    Processes telemetry data and generates controller commands.

    Strategy:
    - Keep constant forward pitch
    - Rotate toward target using yaw
    - Adjust altitude using throttle

    (Ignore roll for now)
    """

    # -----------------------------
    # Configuration parameters
    # -----------------------------

    FORWARD_PITCH = 0.4

    YAW_GAIN = 1.5
    ALTITUDE_GAIN = 0.05

    MAX_YAW_STICK = 1.0
    MAX_THROTTLE = 1.0

    # Reduce speed when badly misaligned
    MAX_YAW_ERROR_FOR_FULL_SPEED = math.radians(45)


    # -----------------------------
    # Geometry
    # -----------------------------

    drone_pos = (
        data.drone_x,
        data.drone_y,
        data.drone_z,
    )

    target_pos = (
        data.target_x,
        data.target_y,
        data.target_z,
    )

    relative = relative_vector(drone_pos, target_pos)

    target_yaw = desired_yaw(relative)


    # Unreal sends degrees, convert to radians
    current_yaw = math.radians(data.drone_yaw)

    error = yaw_error(current_yaw, target_yaw)


    # -----------------------------
    # Yaw controller
    # -----------------------------

    yaw_command = clamp(
        YAW_GAIN * error,
        -MAX_YAW_STICK,
        MAX_YAW_STICK
    )


    # -----------------------------
    # Altitude controller
    # -----------------------------

    altitude_error = data.target_z - data.drone_z

    throttle_command = clamp(
        ALTITUDE_GAIN * altitude_error,
        -MAX_THROTTLE,
        MAX_THROTTLE
    )


    # -----------------------------
    # Forward speed control
    # -----------------------------

    # Slow down while turning sharply
    alignment = abs(error)

    if alignment > MAX_YAW_ERROR_FOR_FULL_SPEED:
        pitch_command = 0.0
    else:
        pitch_command = FORWARD_PITCH

    return ControllerCommand.roll_pitch_yaw_throttle(
        roll=0.0,
        pitch=pitch_command,
        yaw=yaw_command,
        throttle=throttle_command,
    )