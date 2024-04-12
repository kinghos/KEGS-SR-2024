from sr.robot3 import *
from math import pi

robot = Robot()
uno = robot.arduino

CPR = 2 * pi * 1000/ (4*11 * 0.229) # Magic functioning as of 19.03.24
WHEEL_DIAMETER = 80

"""
case 'd': // ENABLE ENCODER
case 'e': // RETURN ENCODER
case 'f': // ENABLE MICROSWITCH
case 'g': // RETURN MICROSWITCH

"""

def getMicroswitch():
    while True:
        robot.sleep(0.05)
        microswitchInfo = uno.command("g") # returns (microswitch_state ? "1" : "0");
        if microswitchInfo:
            print(microswitchInfo)
            if int(microswitchInfo):
                return True
            else:
                return False

def getEncoder():
    while True:
        robot.sleep(0.05)
        encoderInfo = uno.command("e")
        if encoderInfo:
            print(encoderInfo)
            return int(encoderInfo)


def calculateDistance(encoderCount):
    distance = (encoderCount / CPR) * pi * WHEEL_DIAMETER # Distance in mm
    return distance


def enableEncoder():
    uno.command("d")
    return

def enableMicroswitch():
    uno.command("f")
    return

while True:
    print("getting encoder")
    for i in range(0,50):
        print(calculateDistance(getEncoder()))
        robot.sleep(0.1)
    robot.sleep(2)
    print("enabling microswitch")
    enableMicroswitch()
    print("getting microswitch")
    while getMicroswitch() == False:
        getMicroswitch()