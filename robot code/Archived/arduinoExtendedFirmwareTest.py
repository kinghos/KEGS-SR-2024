from sr.robot3 import *

robot = Robot()
mts = robot.motor_board.motors
arduino = robot.arduino

while True:
    mts[0].power = 0.1
    mts[1].power = 0.1
    distance = str(arduino.command("e"))
    # distance = int.from_bytes(arduino.command("e"), "little") # Uses 'e' command to read distance
    print(distance)
    print(distance) # Prints cumulative distance
    robot.sleep(0.1)
