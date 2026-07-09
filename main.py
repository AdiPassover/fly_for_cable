from controller_message import ControllerMessageSender
from telemetry_server import UDPServer
from flight_control import process_telemetry_data
import argparse


def main(telemetry_ip: str, telemetry_port: int, control_protocol: str, control_server_address: tuple, control_usb_port: str):
    sender = ControllerMessageSender(protocol=control_protocol, server_address=control_server_address, usb_port=control_usb_port, clamp_axes=False)
    
    def _handle_telemetry_data(data):
        command = process_telemetry_data(data)
        roll, pitch, yaw, throttle, zoom, mode = command.to_msg()
        print(f"roll={roll}, pitch={pitch}, yaw={yaw}, throttle={throttle}")
        sender.send(roll=roll, pitch=pitch, yaw=yaw, throttle=throttle, camera=zoom, mode=mode)
    
    server = UDPServer(telemetry_ip, telemetry_port, _handle_telemetry_data)
    server.listen()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fly for Cable Application")
    parser.add_argument("--udp_ip", type=str, default="localhost", help="IP address for the UDP server")
    parser.add_argument("--udp_port", type=int, default=9000, help="Port for the UDP server")
    parser.add_argument("--protocol", type=str, default="usb", choices=["usb", "udp"], help="Protocol for controller communication")
    parser.add_argument("--control_port", type=str, default="COM6", help="USB port for the controller")
    parser.add_argument("--control_address", type=str, default=None, help="Address for controller communication (if protocol is udp)")

    args = parser.parse_args()

    if args.control_address:
        control_address = tuple(args.control_address.split(":"))
        control_address = (control_address[0], int(control_address[1]))
    else:
        control_address = ("109.207.78.37", 6001)

    main(args.udp_ip, args.udp_port, args.protocol, control_address, args.control_port)
    


    