from controller_message import ControllerMessageSender


def main():
    sender = ControllerMessageSender(protocol='usb', usb_port="COM6", clamp_axes=False)

    try:
        print("Sending pitch")
        while True:
            sender.send(pitch=1500)
    except KeyboardInterrupt:
        print("\nExiting gracefully.")


if __name__ == "__main__":
    main()