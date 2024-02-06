from sr.robot3 import *
import threading


mts = robot.motor_board.motors
ARDUINO_SN = "" # TODO ADD ARDUINO SN
robot = Robot(ignored_arduinos=[ARDUINO_SN])
arduino = robot.raw_serial_devices[ARDUINO_SN]
serial_port = arduino.port


def readDistance():
    handshake = performHandshake()
    robot.sleep(0.1)
    while not handshake:
        performHandshake()
        robot.sleep(0.1)
    serialInput = arduino.read_until(b"\n")
    distance = int.from_bytes(serialInput, "little")
    return distance

def performHandshake():
    arduino.write(b"FromPi\n")
    response = arduino.read_until(b"\n")
    if response:
        print("Handshake successful")
        return True
    else:
        print("Handshake failed")
        return False

performHandshake()

while True:
    mts[0].power = 0.1
    mts[1].power = 0.1
    distance = readDistance()
    print(distance) # Prints cumulative distance
    robot.sleep(0.1)
