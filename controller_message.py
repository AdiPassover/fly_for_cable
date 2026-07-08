import struct
from dataclasses import dataclass
from time import sleep
from typing import Optional
from enum import Enum


CLOUD_ADDRESS = ("109.207.78.37", 6001)


@dataclass
class ControllerMessage:

    AXES_RANGE = (0, 2000)
    MID_VALUE = (AXES_RANGE[1] - AXES_RANGE[0]) // 2

    class Mode(Enum):
        NONE = 0
        ZOOM_IN = 1
        ZOOM_OUT = 2

        # add drone specific id
        TURN_ON_START = 1000
        BIND_START = 2000

        @staticmethod
        def TURN_ON(drone_id: int) -> int:
            return ControllerMessage.Mode.TURN_ON_START.value + drone_id
        @staticmethod
        def BIND(drone_id: int) -> int:
            return ControllerMessage.Mode.BIND_START.value + drone_id

    def __init__(self, controller_id:Optional[int]=None, roll:int=MID_VALUE, pitch:int=MID_VALUE, yaw:int=MID_VALUE,
                 throttle:int=MID_VALUE, camera:int=MID_VALUE, mode:int=0):
        self.controller_id = controller_id
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.throttle = throttle
        self.camera = camera
        self.mode = mode

    def binary(self, delimiter=False) -> bytes:
        buf = bytearray()

        if self.controller_id is not None:
            buf += struct.pack('<2B', 0, int(self.controller_id))

        buf += struct.pack('<6h', self.roll, self.pitch, self.yaw, self.throttle, self.camera, self.mode)

        if delimiter:
            buf += struct.pack('<1B', ord('\n'))

        return bytes(buf)

    def __str__(self) -> str:
        base = f"(T,Y,P,R,C,M) ==> {self.throttle}\t{self.yaw}\t{self.pitch}\t{self.roll}\t{self.camera}\t{self.mode}"
        if self.controller_id is not None:
            return f"Controller {self.controller_id}: " + base
        return base

    def send_udp(self, sock, server_address=CLOUD_ADDRESS):
        """ Expects a UDP socket """
        sock.sendto(self.binary(), server_address)

    def send_usb(self, ser):
        """ Expects a serial.Serial object """
        ser.write(self.binary(delimiter=True))
        # print serial output for debugging
        # print(ser.readline().decode('utf-8').strip())


def _clamp(value:int) -> int:
    return max(ControllerMessage.AXES_RANGE[0], min(ControllerMessage.AXES_RANGE[1], value))


class ControllerMessageFactory:

    def __init__(self, drone_id:Optional[int]=None, clamp_axes:bool=True):
        self.drone_id = drone_id
        self.clamp_axes = clamp_axes

    def create(self, roll:int=ControllerMessage.MID_VALUE, pitch:int=ControllerMessage.MID_VALUE,
               yaw:int=ControllerMessage.MID_VALUE, throttle:int=ControllerMessage.MID_VALUE,
               camera:int=ControllerMessage.MID_VALUE, mode:int=0) -> ControllerMessage:
        if self.clamp_axes:
            roll = _clamp(roll)
            pitch = _clamp(pitch)
            yaw = _clamp(yaw)
            throttle = _clamp(throttle)
            camera = _clamp(camera)
        return ControllerMessage(controller_id=self.drone_id, roll=roll, pitch=pitch, yaw=yaw,
                                 throttle=throttle, camera=camera, mode=mode)

class ControllerMessageSender:

    def __init__(self, drone_id:Optional[int]=None, protocol:str='udp',
               server_address:Optional[tuple[str,int]]=CLOUD_ADDRESS,
               usb_port:Optional[str]=None, clamp_axes:bool=True):
        """
        :param drone_id: Optional ID for the drone (used in message header)
        :param protocol: Communication protocol ('udp' or 'usb')
        :param server_address: Tuple of (IP, port) for UDP or TCP communication
        :param usb_port: Serial port for USB communication (e.g. "COM3" or "/dev/ttyACM0")
        :param clamp_axes: Whether to clamp axis values to the defined range
        """
        self.protocol = protocol
        self.server_address = server_address
        self.msg_factory = ControllerMessageFactory(drone_id=drone_id, clamp_axes=clamp_axes)

        if protocol == 'udp':
            self._setup_udp()
        elif protocol == 'usb':
            self._setup_usb(usb_port)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")

    def send(self, roll:int=ControllerMessage.MID_VALUE, pitch:int=ControllerMessage.MID_VALUE,
               yaw:int=ControllerMessage.MID_VALUE, throttle:int=ControllerMessage.MID_VALUE,
               camera:int=ControllerMessage.MID_VALUE, mode:int=0):
        msg = self.msg_factory.create(roll=roll, pitch=pitch, yaw=yaw, throttle=throttle, camera=camera, mode=mode)
        self._send(msg)

    def _setup_udp(self):
        import socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def _setup_usb(self, usb_port: str):
        import serial
        self.ser = serial.Serial(port=usb_port, baudrate=115200, timeout=1)

    def _send(self, message:ControllerMessage):
        if self.protocol == 'udp':
            message.send_udp(self.sock, self.server_address)
        elif self.protocol == 'usb':
            message.send_usb(self.ser)



if __name__ == "__main__":
    sender = ControllerMessageSender(drone_id=51, protocol='udp')
    print("Sending")
    while True:
        sender.send(throttle=2000)
        sleep(0.1)
    print("Stopped")

