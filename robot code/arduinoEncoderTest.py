from sr.robot3 import *
import threading


robot = Robot(ignored_arduinos=[ARDUINO_SN])
mts = robot.motor_board.motors
ARDUINO_SN = "" # TODO ADD ARDUINO SN
arduino = robot.raw_serial_devices[ARDUINO_SN]
serial_port = arduino.port

def performHandshake():
    arduino.write(b"FromPi\n")
    response = arduino.read_until(b"\n")
    if response:
        print("Handshake successful")
        return True
    else:
        print("Handshake failed")
        return False

def readDistance():
    handshake = performHandshake()
    robot.sleep(0.1)
    while not handshake:
        performHandshake()
        robot.sleep(0.1)
    serialInput = arduino.read_until(b"\n")
    distance = int.from_bytes(serialInput, "little")
    return distance


while True:
    mts[0].power = 0.1
    mts[1].power = 0.1
    distance = readDistance()
    print(distance) # Prints cumulative distance
