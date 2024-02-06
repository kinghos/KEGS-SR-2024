from sr.robot3 import *
import threading

robot = Robot()
mts = robot.motor_board.motors
arduino = robot.arduino


def readDistance():
    distance = arduino.command("e") # Uses 'e' command to read distance


while True:
    mts[0].power = 0.1
    mts[1].power = 0.1
    distance = readDistance()
    print(distance) # Prints cumulative distance
