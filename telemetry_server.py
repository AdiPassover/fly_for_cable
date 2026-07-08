import socket
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
        if len(data) != 32:
            raise ValueError("Invalid data length for TelemetryData. Expected 32 bytes.")
        
        unpacked_data = struct.unpack('!ffffffff', data)
        return TelemetryData(*unpacked_data)
    
    def __str__(self):
        return (f"Drone Position: ({self.drone_x}, {self.drone_y}, {self.drone_z}), "
                f"Orientation: (Pitch: {self.drone_pitch}, Yaw: {self.drone_yaw}, Roll: {self.drone_roll}), "
                f"Target Position: ({self.target_x}, {self.target_y}, {self.target_z})")



class UDPServer:
    def __init__(self, host: str, port: int, on_data_received: callable[TelemetryData]):
        """
        Initializes the UDP server and starts listening for incoming data.

        :param host: The host IP address to bind the server to.
        :param port: The port number to bind the server to.
        :param on_data_received: A callback function to handle received data.
        """
        self.host = host
        self.port = port
        self.on_data_received = on_data_received
        self.running = True

        # Create a socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        self.listen()

    def listen(self):
        """Listens for incoming UDP data."""
        print(f"Server listening on {self.host}:{self.port}")
        try:
            while self.running:
                data, _ = self.sock.recvfrom(1024)
                self.on_data_received(TelemetryData.from_bytes(data))
        except KeyboardInterrupt:
            print("Server shutting down...")
            self.running = False
        finally:
            self.sock.close()
        



if __name__ == "__main__":

    def print_data(data):
        print(f"Data received: {data.decode()}")
    
    server = UDPServer("localhost", 9999, print_data)