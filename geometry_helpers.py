import math


def wrap_angle(angle):
    """Wrap angle to [-pi, pi]."""
    return (angle + math.pi) % (2 * math.pi) - math.pi


def relative_vector(drone_pos, target_pos):
    return (
        target_pos[0] - drone_pos[0],
        target_pos[1] - drone_pos[1],
        target_pos[2] - drone_pos[2],
    )


def horizontal_distance(vec):
    return math.hypot(vec[0], vec[1])


def distance(vec):
    return math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)


def desired_yaw(vec):
    return math.atan2(vec[1], vec[0])


def desired_pitch(vec):
    h = horizontal_distance(vec)
    return math.atan2(vec[2], h)


def yaw_error(current_yaw, desired):
    return wrap_angle(desired - current_yaw)