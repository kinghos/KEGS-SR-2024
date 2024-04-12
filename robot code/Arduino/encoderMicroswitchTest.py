from sr.robot3 import *

robot = Robot()
uno = robot.arduino


"""
case 'e': // RETURN ENCODER
case 'f': // ENABLE MICROSWITCH
case 'g': // RETURN MICROSWITCH
case 'h': // ENABLE ENCODER
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
            return(encoderInfo)

def enableEncoder():
    uno.command("h")
    return

def enableMicroswitch():
    uno.command("f")
    return

while True:
    print("getting encoder")
    for i in range(0,50):
        getEncoder()
        robot.sleep(0.1)
    robot.sleep(1)
    print("enabling microswitch")
    enableMicroswitch()
    print("getting microswitch")
    while getMicroswitch() == False:
        getMicroswitch()