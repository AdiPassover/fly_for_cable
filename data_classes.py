from dataclasses import dataclass
import struct


@dataclass
class TelemetryData:
    
    drone_x: float
    drone_y: float
    drone_z: float
    
    drone_pitch: float
    drone_yaw: float
    drone_roll: float

    target_x: float
    target_y: float
    target_z: float

    @staticmethod
    def from_bytes(data: bytes) -> 'TelemetryData':
        """
        Converts bytes data to a TelemetryData instance.

        :param data: The bytes data to convert.
        :return: A TelemetryData instance.
        """
        if len(data) != 36:
            raise ValueError(f"Invalid data length ({len(data)}) for TelemetryData. Expected 36 bytes.")
        
        unpacked_data = struct.unpack('<9f', data)
        return TelemetryData(*unpacked_data)
    
    def __str__(self):
        return (f"Drone Position: ({self.drone_x}, {self.drone_y}, {self.drone_z}), "
                f"Orientation: (Pitch: {self.drone_pitch}, Yaw: {self.drone_yaw}, Roll: {self.drone_roll}), "
                f"Target Position: ({self.target_x}, {self.target_y}, {self.target_z})")


@dataclass
class ControllerCommand:

    roll: float
    pitch: float
    yaw: float
    throttle: float
    zoom: float
    mode: int

    @staticmethod
    def roll_pitch_yaw_throttle(roll: float, pitch: float, yaw: float, throttle: float) -> 'ControllerCommand':
        return ControllerCommand(roll, pitch, yaw, throttle, 0.0, 0)

    def to_msg(self):

        def _normalize_to_msg_range(value):
            return int((value + 1) * 1000)
        return _normalize_to_msg_range(self.roll), _normalize_to_msg_range(self.pitch), _normalize_to_msg_range(self.yaw), _normalize_to_msg_range(self.throttle), _normalize_to_msg_range(self.zoom), self.mode
        