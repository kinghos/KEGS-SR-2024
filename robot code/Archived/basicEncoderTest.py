from sr.robot3 import *
import math

robot = Robot()
mts = robot.motor_board.motors
arduino = robot.arduino

CPR = 2 * math.pi * 1000/ (4*11 * 0.229)
WHEEL_DIAMETER = 80
encoderCount = 0

mts[0].power = 0.25
mts[1].power = 0.25
while True:
    robot.sleep(0.1)
    strEncoderCount = arduino.command("e")
    if strEncoderCount: # Checks for non-empty string
        encoderCount = float(strEncoderCount)
        distance = (encoderCount / CPR) * math.pi * WHEEL_DIAMETER # Distance in mm
        print(f"Count: {encoderCount},\t Distance: {distance}mm")
    