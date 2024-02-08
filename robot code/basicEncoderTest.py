from sr.robot3 import *

robot = Robot()
mts = robot.motor_board.motors
arduino = robot.arduino

while True:
    mts[0].power = 0.25
    mts[1].power = 0.25
    distance = str(arduino.command("v"))
    print(distance) # Prints cumulative distance
    robot.sleep(0.1)
