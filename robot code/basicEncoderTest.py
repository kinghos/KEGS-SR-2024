from sr.robot3 import *
import math

robot = Robot()
mts = robot.motor_board.motors
arduino = robot.arduino

CPR = 2 * math.pi / (4 * 11)
WHEEL_DIAMETER = 80
encoderCount = 0

mts[0].power = 0.25
mts[1].power = 0.25
while True:
    encoderCount = int(arduino.command("v"))
    distance = (encoderCount / CPR) * math.pi * WHEEL_DIAMETER
    print(f"Count: {encoderCount},\t Distance: {distance}mm")
    robot.sleep(0.1)
    
